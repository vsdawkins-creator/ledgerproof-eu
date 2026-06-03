"""Side-channel receipt emitters.

Constraint C7: receipts emit on a side channel, never modifying the DeepSeek
response payload. Choose the emitter that fits your infra:

- `LogEmitter`     — JSON line to stdout / a logger (default; great for dev)
- `StderrEmitter`  — JSON line to stderr (handy when stdout carries app data)
- `WebhookEmitter` — HTTP POST to an internal receipt-ingest URL
- `QueueEmitter`   — push onto an in-process `queue.Queue` (testing / batching)
- `MultiEmitter`   — fan out to several emitters (e.g. log + webhook)
"""

from __future__ import annotations

import json
import logging
import queue
import sys
import urllib.request
from typing import Any, Iterable, Protocol


class Emitter(Protocol):
    """Side-channel emitter protocol."""

    def emit(self, envelope: dict[str, Any]) -> None: ...


class LogEmitter:
    """Emit a JSON line to a logger (or stdout)."""

    def __init__(self, logger: logging.Logger | None = None, stream=None) -> None:
        self._logger = logger
        self._stream = stream if stream is not None else sys.stdout

    def emit(self, envelope: dict[str, Any]) -> None:
        line = json.dumps(envelope, sort_keys=True, default=str)
        if self._logger is not None:
            self._logger.info("ledgerproof.receipt %s", line)
        else:
            print(line, file=self._stream, flush=True)


class StderrEmitter:
    """Emit a JSON line to stderr. Useful when stdout is reserved for the
    application's own structured output (e.g. CLI tools).
    """

    def __init__(self) -> None:
        self._stream = sys.stderr

    def emit(self, envelope: dict[str, Any]) -> None:
        line = json.dumps(envelope, sort_keys=True, default=str)
        print(line, file=self._stream, flush=True)


class WebhookEmitter:
    """POST the envelope as JSON to `url`. Best-effort; failures are logged
    but never raised — the receipt MUST NOT interfere with the user-facing
    DeepSeek call.
    """

    def __init__(self, url: str, timeout: float = 2.0) -> None:
        self.url = url
        self.timeout = timeout
        self._log = logging.getLogger("ledgerproof.webhook")

    def emit(self, envelope: dict[str, Any]) -> None:
        try:
            data = json.dumps(envelope, sort_keys=True, default=str).encode("utf-8")
            req = urllib.request.Request(
                self.url,
                data=data,
                headers={"content-type": "application/json"},
                method="POST",
            )
            urllib.request.urlopen(req, timeout=self.timeout).close()
        except Exception as exc:  # noqa: BLE001
            self._log.warning("webhook emit failed: %s", exc)


class QueueEmitter:
    """Drop the envelope onto an in-process queue. Useful for tests and for
    Merkle-batching workers that flush to an anchoring service.
    """

    def __init__(self, q: queue.Queue | None = None) -> None:
        self.q = q if q is not None else queue.Queue()

    def emit(self, envelope: dict[str, Any]) -> None:
        self.q.put(envelope)


class MultiEmitter:
    """Fan-out to multiple emitters. Each child's failure is isolated — one
    misbehaving emitter MUST NOT prevent the others from receiving the
    envelope, and MUST NOT raise into the caller path (C7).
    """

    def __init__(self, emitters: Iterable[Emitter]) -> None:
        self.emitters = list(emitters)
        self._log = logging.getLogger("ledgerproof.multi")

    def emit(self, envelope: dict[str, Any]) -> None:
        for emitter in self.emitters:
            try:
                emitter.emit(envelope)
            except Exception as exc:  # noqa: BLE001
                self._log.warning("emitter %r failed: %s", emitter, exc)
