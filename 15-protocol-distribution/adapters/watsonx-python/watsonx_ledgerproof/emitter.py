"""
Side-channel emitters (constraint C7).

Receipts NEVER ride inside the watsonx.ai response payload. They go to one of:
  - LogEmitter — structured stdout/stderr/logger
  - WebhookEmitter — HTTPS POST to deployer-controlled endpoint
  - QueueEmitter — generic callable interface, suitable for Kafka/MQ/Redis
  - IbmCloudLogsEmitter — convenience wrapper around a deployer-supplied IBM
    Cloud Logs (LogDNA-derived) ingest callable; kept as a thin shim so
    deployers can plug in their own client.

All emitters are best-effort. Failure to emit MUST NOT raise into the calling
application's response path (we swallow + log).
"""

from __future__ import annotations

import json
import logging
import sys
from typing import Any, Callable, Protocol, runtime_checkable
from urllib import error as urlerror
from urllib import request as urlrequest

logger = logging.getLogger("watsonx_ledgerproof.emitter")


@runtime_checkable
class Emitter(Protocol):
    def emit(self, signed_receipt: dict[str, Any]) -> None: ...


class LogEmitter:
    """Emit JSON-encoded signed receipts to a logger (stdout by default)."""

    def __init__(self, stream=None, logger_name: str = "ledgerproof.receipt"):
        self._stream = stream
        self._logger = logging.getLogger(logger_name)

    def emit(self, signed_receipt: dict[str, Any]) -> None:
        try:
            line = json.dumps(signed_receipt, default=str, separators=(",", ":"))
        except (TypeError, ValueError) as exc:  # pragma: no cover
            logger.warning("LogEmitter could not serialize receipt: %s", exc)
            return
        if self._stream is not None:
            self._stream.write(line + "\n")
            self._stream.flush()
        else:
            self._logger.info(line)


class WebhookEmitter:
    """POST signed receipt JSON to a deployer-controlled HTTPS endpoint."""

    def __init__(
        self,
        url: str,
        timeout_seconds: float = 2.0,
        headers: dict[str, str] | None = None,
    ):
        if not url.startswith(("http://", "https://")):
            raise ValueError("WebhookEmitter url must be http(s)://")
        self.url = url
        self.timeout_seconds = timeout_seconds
        self.headers = {"Content-Type": "application/json", **(headers or {})}

    def emit(self, signed_receipt: dict[str, Any]) -> None:
        try:
            body = json.dumps(signed_receipt, default=str).encode("utf-8")
            req = urlrequest.Request(
                self.url, data=body, headers=self.headers, method="POST"
            )
            with urlrequest.urlopen(req, timeout=self.timeout_seconds) as resp:
                resp.read()
        except (urlerror.URLError, TimeoutError, OSError) as exc:
            logger.warning("WebhookEmitter failed to POST receipt: %s", exc)


class QueueEmitter:
    """Wrap any callable (lambda, MQ producer, Kafka producer.send, ...)."""

    def __init__(self, sink: Callable[[dict[str, Any]], None]):
        self._sink = sink

    def emit(self, signed_receipt: dict[str, Any]) -> None:
        try:
            self._sink(signed_receipt)
        except Exception as exc:  # noqa: BLE001 — best-effort by design
            logger.warning("QueueEmitter sink raised: %s", exc)


class IbmCloudLogsEmitter:
    """
    Thin wrapper over a deployer-supplied IBM Cloud Logs ingest callable.

    Example (using the official `ibmcloud-logs-router-sdk` or an HTTP client):

        def ingest(line: str) -> None:
            requests.post(
                "https://logs.eu-de.cloud.ibm.com/logs/v1/singles",
                headers={"Authorization": f"Bearer {iam_token}"},
                json={"lines": [{"line": line, "app": "ledgerproof"}]},
                timeout=2.0,
            )

        emitter = IbmCloudLogsEmitter(ingest_fn=ingest)
    """

    def __init__(self, ingest_fn: Callable[[str], None]):
        self._ingest = ingest_fn

    def emit(self, signed_receipt: dict[str, Any]) -> None:
        try:
            line = json.dumps(signed_receipt, default=str, separators=(",", ":"))
            self._ingest(line)
        except Exception as exc:  # noqa: BLE001
            logger.warning("IbmCloudLogsEmitter failed: %s", exc)


class MultiEmitter:
    """Fan out a receipt to multiple emitters."""

    def __init__(self, *emitters: Emitter):
        self._emitters = emitters

    def emit(self, signed_receipt: dict[str, Any]) -> None:
        for em in self._emitters:
            try:
                em.emit(signed_receipt)
            except Exception as exc:  # noqa: BLE001
                logger.warning("MultiEmitter child %r raised: %s", em, exc)


class StderrEmitter(LogEmitter):
    """Convenience: log to stderr."""

    def __init__(self):
        super().__init__(stream=sys.stderr)
