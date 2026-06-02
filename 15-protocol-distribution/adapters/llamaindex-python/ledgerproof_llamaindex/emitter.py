"""Side-channel emitters for LedgerProof receipts.

Per protocol invariant C7, receipts MUST NOT be folded back into the LlamaIndex
response. They go out to a separate channel: a log line, a webhook, or a queue.
That separation is what lets the LedgerProof Foundation verify receipts offline
without ever seeing your model traffic.

Three implementations ship in the MVP:

- ``LogEmitter`` — JSON to a Python logger. Cheap, structural, good for dev.
- ``WebhookEmitter`` — POST canonical CBOR to a URL. Use a real HTTP client
  in production (httpx with retry/circuit-breaker, not stdlib urllib).
- ``QueueEmitter`` — push onto any ``queue.Queue``-like object. Pairs well
  with a sidecar that batches and Merkle-roots before Bitcoin anchoring.
"""

from __future__ import annotations

import abc
import json
import logging
import queue as _queue
import urllib.error
import urllib.request
from typing import Any, Optional

from .canonical import canonical_cbor

logger = logging.getLogger("ledgerproof.llamaindex")


class Emitter(abc.ABC):
    """Common interface every emitter satisfies."""

    @abc.abstractmethod
    def emit(self, envelope: dict[str, Any]) -> None:
        """Send the signed receipt envelope to the side channel."""

    def close(self) -> None:
        """Flush / release resources. Default no-op."""


class LogEmitter(Emitter):
    """Write the envelope as a single JSON line to a logger.

    Defaults to the ``ledgerproof.llamaindex`` logger at INFO. Configure the
    logger like any other Python logger; the emitter doesn't touch handlers.
    """

    def __init__(
        self,
        log: Optional[logging.Logger] = None,
        level: int = logging.INFO,
    ):
        self._log = log or logger
        self._level = level

    def emit(self, envelope: dict[str, Any]) -> None:
        try:
            line = json.dumps(envelope, sort_keys=True, separators=(",", ":"))
        except (TypeError, ValueError):
            # Last-resort fallback so we never raise out of a callback.
            line = json.dumps({"envelope_repr": repr(envelope)})
        self._log.log(self._level, "ledgerproof_receipt %s", line)


class WebhookEmitter(Emitter):
    """POST the canonical-CBOR envelope to a URL.

    MVP uses ``urllib.request`` to avoid pulling httpx into the base package.
    For production swap in httpx + retries + circuit breaker; the interface is
    the same.
    """

    def __init__(
        self,
        url: str,
        *,
        timeout_s: float = 5.0,
        extra_headers: Optional[dict[str, str]] = None,
    ):
        if not url.startswith(("http://", "https://")):
            raise ValueError("WebhookEmitter url must be http(s)://")
        self._url = url
        self._timeout = timeout_s
        self._headers = {
            "Content-Type": "application/cbor",
            "User-Agent": "ledgerproof-llamaindex/0.1",
        }
        if extra_headers:
            self._headers.update(extra_headers)

    def emit(self, envelope: dict[str, Any]) -> None:
        body = canonical_cbor(envelope)
        req = urllib.request.Request(self._url, data=body, headers=self._headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                # Drain so the socket can be reused; ignore body.
                resp.read(1024)
        except (urllib.error.URLError, TimeoutError) as exc:
            # Per C7 we must NEVER let an emitter failure break the user request.
            logger.warning("WebhookEmitter POST failed: %s", exc)


class QueueEmitter(Emitter):
    """Push the envelope onto a queue for an out-of-process worker.

    Accepts anything with a ``put(item, block, timeout)`` method —
    ``queue.Queue``, ``multiprocessing.Queue``, or a thin wrapper around your
    favourite broker (Redis, Kafka, SQS).
    """

    def __init__(self, sink: Any, *, block: bool = False, timeout_s: Optional[float] = None):
        if not hasattr(sink, "put"):
            raise TypeError("QueueEmitter sink must have a .put() method")
        self._sink = sink
        self._block = block
        self._timeout = timeout_s

    def emit(self, envelope: dict[str, Any]) -> None:
        try:
            self._sink.put(envelope, self._block, self._timeout)
        except _queue.Full as exc:
            # C7: never break the caller. Drop + log.
            logger.warning("QueueEmitter sink full, dropping receipt: %s", exc)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("QueueEmitter put failed: %s", exc)
