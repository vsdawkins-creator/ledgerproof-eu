"""Manual receipt emission API.

Used when callers want explicit control rather than the Cortex wrapper or
decorator. Always emits via side-channel (C7).
"""

from __future__ import annotations

import time
from typing import Any, Optional

from .emitter import AsyncEmitter, ReceiptSink, build_signed_receipt, default_sink_from_env
from .schema import ReceiptSchemaName, resolve_schema
from .signer import Ed25519Signer, SignedReceipt

_DEFAULT_EMITTER: Optional[AsyncEmitter] = None


def _get_default_emitter(sink: Optional[ReceiptSink] = None) -> AsyncEmitter:
    global _DEFAULT_EMITTER
    if _DEFAULT_EMITTER is None:
        _DEFAULT_EMITTER = AsyncEmitter(sink or default_sink_from_env())
    return _DEFAULT_EMITTER


def emit_receipt(
    schema: str | ReceiptSchemaName,
    *,
    signer: Ed25519Signer,
    deployer_id: str,
    model: str,
    sink: Optional[ReceiptSink] = None,
    emitter: Optional[AsyncEmitter] = None,
    fields: Optional[dict[str, Any]] = None,
) -> SignedReceipt:
    """Build, sign, and asynchronously emit a receipt.

    Returns the SignedReceipt for tests / introspection. The actual sink
    write happens on a background thread (C7).
    """
    fields = fields or {}
    payload = {
        "deployer_id": deployer_id,
        "model": model,
        "timestamp_unix_ms": int(time.time() * 1000),
        **fields,
    }
    schema_cls = resolve_schema(schema)
    receipt = schema_cls(**payload)
    signed = build_signed_receipt(receipt, signer)
    em = emitter or _get_default_emitter(sink)
    em.submit(signed)
    return signed
