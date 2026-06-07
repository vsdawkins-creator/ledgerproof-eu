"""Side-channel emitters (C7).

An emitter accepts a fully-formed, signed receipt dict and delivers it to a
side-channel sink. The default ``StdoutEmitter`` writes JSON-Lines to stdout.

The contract is intentionally trivial so that production deployments can plug
in Kafka, S3, SQS, Pub/Sub, or a Foundation-operated witness.
"""

from __future__ import annotations

import json
import sys
from typing import Any, Callable, Mapping, Protocol


class Emitter(Protocol):
    def emit(self, receipt: Mapping[str, Any]) -> None: ...


class StdoutEmitter:
    """Writes JSON-Lines to ``sys.stdout`` (default)."""

    def __init__(self, *, stream=None) -> None:
        self._stream = stream or sys.stdout

    def emit(self, receipt: Mapping[str, Any]) -> None:
        self._stream.write(json.dumps(receipt, separators=(",", ":")) + "\n")
        try:
            self._stream.flush()
        except Exception:
            pass


class InMemoryEmitter:
    """Keeps every emitted receipt in memory — handy for tests and demos."""

    def __init__(self) -> None:
        self.receipts: list[Mapping[str, Any]] = []

    def emit(self, receipt: Mapping[str, Any]) -> None:
        self.receipts.append(receipt)

    def __len__(self) -> int:
        return len(self.receipts)


class CallableEmitter:
    """Wraps any ``Callable[[Mapping], None]`` into an Emitter."""

    def __init__(self, fn: Callable[[Mapping[str, Any]], None]) -> None:
        self._fn = fn

    def emit(self, receipt: Mapping[str, Any]) -> None:
        self._fn(receipt)
