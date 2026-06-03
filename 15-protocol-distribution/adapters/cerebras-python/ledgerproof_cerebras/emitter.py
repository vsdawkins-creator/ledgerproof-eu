"""Side-channel receipt emitter.

C7: never block, never alter the inference response. Emission runs in a
background daemon thread; failures are logged and dropped, never raised.
"""

from __future__ import annotations

import json
import logging
import os
import queue
import threading
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from .canonical import canonical_cbor
from .schema import _ReceiptBase
from .signer import Ed25519Signer, SignedReceipt
from .version import ADAPTER_NAME, PROTOCOL_VERSION

logger = logging.getLogger("ledgerproof_cerebras.emitter")


class ReceiptSink(ABC):
    @abstractmethod
    def write(self, receipt: SignedReceipt) -> None: ...


class StdoutSink(ReceiptSink):
    def write(self, receipt: SignedReceipt) -> None:
        print(f"[ledgerproof-cerebras receipt] {json.dumps(receipt.to_dict())}")


class FileSink(ReceiptSink):
    """Append-only JSONL sink."""

    def __init__(self, path: str | Path):
        self._path = Path(path)
        self._lock = threading.Lock()
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, receipt: SignedReceipt) -> None:
        line = json.dumps(receipt.to_dict()) + "\n"
        with self._lock:
            with self._path.open("a", encoding="utf-8") as f:
                f.write(line)


class NullSink(ReceiptSink):
    def write(self, receipt: SignedReceipt) -> None:
        return None


def _envelope(payload: dict) -> dict:
    return {
        "lpr": PROTOCOL_VERSION,
        "adapter": ADAPTER_NAME,
        "payload": payload,
    }


def build_signed_receipt(
    receipt: _ReceiptBase, signer: Ed25519Signer
) -> SignedReceipt:
    envelope = _envelope(receipt.model_dump(mode="json"))
    cbor = canonical_cbor(envelope)
    sig = signer.sign(cbor)
    return SignedReceipt(
        payload_cbor=cbor,
        signature=sig,
        public_key_b64=signer.public_key_b64,
    )


class AsyncEmitter:
    """Background-thread emitter — C7 side-channel guarantee.

    The inference call returns to the caller before this emitter touches
    the sink.
    """

    def __init__(self, sink: ReceiptSink, *, max_queue: int = 1024):
        self._sink = sink
        self._q: "queue.Queue[Optional[SignedReceipt]]" = queue.Queue(maxsize=max_queue)
        self._stop = threading.Event()
        self._thread = threading.Thread(
            target=self._run, name="lpr-cerebras-emitter", daemon=True
        )
        self._thread.start()

    def submit(self, receipt: SignedReceipt) -> None:
        try:
            self._q.put_nowait(receipt)
        except queue.Full:
            # Side-channel must never block hot path; drop with warning.
            logger.warning("LedgerProof emitter queue full; dropping receipt.")

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                item = self._q.get(timeout=0.5)
            except queue.Empty:
                continue
            if item is None:
                return
            try:
                self._sink.write(item)
            except Exception as exc:  # noqa: BLE001
                logger.error("Receipt sink write failed: %s", exc)

    def flush(self, timeout: float = 5.0) -> None:
        deadline = time.monotonic() + timeout
        while not self._q.empty() and time.monotonic() < deadline:
            time.sleep(0.01)

    def close(self) -> None:
        self._stop.set()
        try:
            self._q.put_nowait(None)
        except queue.Full:
            pass
        self._thread.join(timeout=2.0)


def default_sink_from_env() -> ReceiptSink:
    target = os.environ.get("LEDGERPROOF_SINK", "stdout").lower()
    if target == "stdout":
        return StdoutSink()
    if target == "null":
        return NullSink()
    if target.startswith("file:"):
        return FileSink(target.split(":", 1)[1])
    return StdoutSink()
