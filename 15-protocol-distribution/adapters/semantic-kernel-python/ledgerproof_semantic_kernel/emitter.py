"""Side-channel receipt emitters (C7: side-channel emission only).

All emitters share a common interface: `emit(receipt: dict) -> None`. The
receipt dict already contains the canonical body + signature + public key.
Emitters MUST NOT mutate the receipt and MUST NOT block the LLM response
path in surprising ways.
"""

from __future__ import annotations

import json
import queue
import threading
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Mapping, Optional
from urllib import request as _urlrequest


class BaseEmitter(ABC):
    """Common emitter interface."""

    @abstractmethod
    def emit(self, receipt: Mapping[str, Any]) -> None:
        """Send the receipt over the side channel."""


class LogEmitter(BaseEmitter):
    """Append each receipt as a JSON line to a file.

    Thread-safe. Creates the file (and parent directory) on first write.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._lock = threading.Lock()

    def emit(self, receipt: Mapping[str, Any]) -> None:
        line = json.dumps(dict(receipt), sort_keys=True, separators=(",", ":"))
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(line)
                fh.write("\n")


class WebhookEmitter(BaseEmitter):
    """POST each receipt to an HTTPS endpoint as a JSON body.

    Uses stdlib urllib to avoid forcing a `requests` dependency. Production
    deployments should wrap this in a worker queue to keep webhook latency
    off the LLM response path.
    """

    def __init__(self, url: str, timeout_seconds: float = 5.0) -> None:
        if not url.startswith(("http://", "https://")):
            raise ValueError(
                f"WebhookEmitter URL must start with http(s)://, got {url!r}"
            )
        self.url = url
        self.timeout_seconds = timeout_seconds

    def emit(self, receipt: Mapping[str, Any]) -> None:
        body = json.dumps(
            dict(receipt), sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        req = _urlrequest.Request(
            self.url,
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "User-Agent": "ledgerproof-semantic-kernel/0.1.0",
            },
        )
        try:
            with _urlrequest.urlopen(req, timeout=self.timeout_seconds) as _:
                pass
        except Exception:
            # Receipt-delivery failure is a separate operational concern
            # from the live response. Phase 2 will add DLQ + retries.
            pass


class QueueEmitter(BaseEmitter):
    """Push receipts onto an in-process `queue.Queue`.

    Useful for tests and for handing off to a background worker thread.
    """

    def __init__(
        self, q: Optional["queue.Queue[Mapping[str, Any]]"] = None
    ) -> None:
        self.queue: "queue.Queue[Mapping[str, Any]]" = (
            q if q is not None else queue.Queue()
        )

    def emit(self, receipt: Mapping[str, Any]) -> None:
        self.queue.put(dict(receipt))
