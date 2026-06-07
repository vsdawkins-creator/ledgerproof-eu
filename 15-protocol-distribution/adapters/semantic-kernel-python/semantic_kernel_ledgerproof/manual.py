"""Manual receipt emission.

The filters and chat-service wrapper cover the standard Semantic Kernel
integration paths. For everything else (custom orchestration, native code
paths that bypass the kernel, post-hoc receipts for batch workloads),
`emit_receipt()` is the low-ceremony manual API.
"""

from __future__ import annotations

import base64
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional

from .canonical import canonical_encode
from .emitter import BaseEmitter, LogEmitter
from .schema import get_schema
from .signer import BaseSigner, Ed25519Signer


def _utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="microseconds")
        .replace("+00:00", "Z")
    )


def emit_receipt(
    *,
    schema_id: str,
    deployer_id: str,
    transcript: str | bytes,
    fields: Optional[Mapping[str, Any]] = None,
    emitter: Optional[BaseEmitter] = None,
    signer: Optional[BaseSigner] = None,
    run_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Build, validate, sign, and emit a single receipt.

    Parameters
    ----------
    schema_id:
        One of the registered LedgerProof schemas (see `schema.SCHEMAS`).
    deployer_id:
        Pseudonymous deployer identifier. MUST NOT be an email.
    transcript:
        The transcript material to hash (str or bytes). Only its SHA-256 is
        recorded; the content is not retained inside the receipt.
    fields:
        Schema-specific fields (e.g. `model_identifier`, `tenant_id`).
    emitter:
        BaseEmitter implementation. Defaults to LogEmitter writing to
        './ledgerproof-receipts.jsonl' in CWD.
    signer:
        BaseSigner implementation. Defaults to ephemeral Ed25519Signer.
    run_id:
        Optional explicit run id. If omitted, a UUID4 is generated.

    Returns
    -------
    The signed receipt envelope (also passed to the emitter).
    """
    emitter = emitter or LogEmitter("./ledgerproof-receipts.jsonl")
    signer = signer or Ed25519Signer()

    if isinstance(transcript, str):
        transcript_bytes = transcript.encode("utf-8")
    elif isinstance(transcript, (bytes, bytearray)):
        transcript_bytes = bytes(transcript)
    else:
        raise TypeError("transcript must be str or bytes")

    transcript_sha256 = hashlib.sha256(transcript_bytes).hexdigest()

    receipt_fields: Dict[str, Any] = {
        "schema_id": schema_id,
        "run_id": run_id or str(uuid.uuid4()),
        "timestamp_utc": _utc_now(),
        "deployer_id": deployer_id,
        "transcript_sha256": transcript_sha256,
    }
    if fields:
        receipt_fields.update(fields)

    validated = get_schema(schema_id)(**receipt_fields).model_dump()

    body_bytes = canonical_encode(validated)
    body_digest = hashlib.sha256(body_bytes).digest()
    signature = signer.sign(body_digest)

    envelope: Dict[str, Any] = {
        "body": validated,
        "body_sha256": body_digest.hex(),
        "signature_ed25519": base64.urlsafe_b64encode(signature)
        .rstrip(b"=")
        .decode("ascii"),
        "public_key_ed25519": signer.public_key_b64(),
        "alg": "Ed25519",
    }
    emitter.emit(envelope)
    return envelope
