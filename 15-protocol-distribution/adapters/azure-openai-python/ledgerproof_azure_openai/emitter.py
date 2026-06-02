"""Side-channel receipt emitters.

Constraint C7: receipts emit on a side channel, never modifying the Azure
OpenAI response payload. Choose the emitter that fits your infra:

- `LogEmitter`     — JSON line to stdout / a logger (default; great for dev)
- `WebhookEmitter` — HTTP POST to an internal receipt-ingest URL
- `QueueEmitter`   — push onto an in-process `queue.Queue` (testing / batching)

Planned for v0.2: `EventHubsEmitter`, `ServiceBusEmitter`, `StorageBlobEmitter`
for native Azure sinks.
"""

from __future__ import annotations

import json
import logging
import queue
import sys
import urllib.request
from typing import Any, Protocol


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


class WebhookEmitter:
    """POST the envelope as JSON to `url`. Best-effort; failures are logged
    but never raised — the receipt MUST NOT interfere with the user-facing
    Azure OpenAI call.
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
