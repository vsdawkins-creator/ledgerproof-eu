"""Side-channel receipt emission.

C7: receipts NEVER mutate the user-facing model output. They are written
to a configurable sink (filesystem by default, in-memory for tests, or any
caller-supplied callable).
"""

from __future__ import annotations

import json
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any, Callable
from weakref import WeakValueDictionary

from .canonical import canonical_cbor

# Process-wide registry so emitters survive Haystack's deepcopy of component
# init kwargs. Components store an emitter_id; we look up the live instance.
_EMITTER_REGISTRY: WeakValueDictionary[str, "Emitter"] = WeakValueDictionary()
_REG_LOCK = Lock()


def register_emitter(emitter: "Emitter") -> str:
    """Insert `emitter` into the process registry and return its id."""
    with _REG_LOCK:
        eid = getattr(emitter, "_lpr_emitter_id", None) or str(uuid.uuid4())
        emitter._lpr_emitter_id = eid  # type: ignore[attr-defined]
        _EMITTER_REGISTRY[eid] = emitter
        return eid


def get_registered_emitter(emitter_id: str) -> "Emitter | None":
    with _REG_LOCK:
        return _EMITTER_REGISTRY.get(emitter_id)


class Emitter(ABC):
    """Base emitter — receives a signed envelope dict and persists it.

    Emitters auto-register in a process-wide weak registry, and return
    themselves from `__deepcopy__` so Haystack's component-arg deepcopy
    does not split the sink into independent copies.
    """

    def __init__(self) -> None:
        register_emitter(self)

    def __deepcopy__(self, memo: dict[int, Any]) -> "Emitter":
        # Side-channel emitters are intentionally shared singletons.
        return self

    def __copy__(self) -> "Emitter":
        return self

    @abstractmethod
    def emit(self, envelope: dict[str, Any]) -> None: ...


class FileEmitter(Emitter):
    """Append-only filesystem sink. One CBOR-encoded receipt per file."""

    def __init__(self, directory: str | Path):
        super().__init__()
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def emit(self, envelope: dict[str, Any]) -> None:
        receipt_id = envelope["receipt"]["receipt_id"]
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S%f")
        path = self.directory / f"{ts}-{receipt_id}.cbor"
        with self._lock:
            path.write_bytes(canonical_cbor(envelope))


class MemoryEmitter(Emitter):
    """In-memory sink. Useful for tests and structured pipelines."""

    def __init__(self) -> None:
        super().__init__()
        self.records: list[dict[str, Any]] = []
        self._lock = Lock()

    def emit(self, envelope: dict[str, Any]) -> None:
        with self._lock:
            self.records.append(envelope)

    def __len__(self) -> int:
        return len(self.records)

    def clear(self) -> None:
        with self._lock:
            self.records.clear()


class JSONLEmitter(Emitter):
    """Newline-delimited JSON sink (CBOR base64-wrapped for human inspection)."""

    def __init__(self, path: str | Path):
        super().__init__()
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def emit(self, envelope: dict[str, Any]) -> None:
        line = json.dumps(envelope, default=str, sort_keys=True)
        with self._lock, self.path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")


class CallableEmitter(Emitter):
    """Wrap any `Callable[[dict], None]` (e.g. OTel exporter, S3 PUT)."""

    def __init__(self, fn: Callable[[dict[str, Any]], None]):
        super().__init__()
        self._fn = fn

    def emit(self, envelope: dict[str, Any]) -> None:
        self._fn(envelope)
