"""Manual receipt emission helper.

For paths where wrapping the upstream client or applying a decorator is awkward —
batch jobs, post-hoc audit trails, third-party adapters — ``emit_receipt`` builds,
signs, and emits a receipt in one call.
"""

from __future__ import annotations

import base64
import time
from typing import Any, Mapping, Optional

from .canonical import sha256_hex
from .emitter import Emitter, StdoutEmitter
from .schema import schema_for
from .signer import EphemeralEd25519Signer
from .version import PROTOCOL_VERSION


_DEFAULT_SIGNER: Optional[EphemeralEd25519Signer] = None
_DEFAULT_EMITTER: Optional[Emitter] = None


def _default_signer() -> EphemeralEd25519Signer:
    global _DEFAULT_SIGNER
    if _DEFAULT_SIGNER is None:
        _DEFAULT_SIGNER = EphemeralEd25519Signer()
    return _DEFAULT_SIGNER


def _default_emitter() -> Emitter:
    global _DEFAULT_EMITTER
    if _DEFAULT_EMITTER is None:
        _DEFAULT_EMITTER = StdoutEmitter()
    return _DEFAULT_EMITTER


def emit_receipt(
    *,
    article: str,
    schema: str,
    prompt_text: str,
    completion_text: str,
    model: str,
    model_version: Optional[str] = None,
    extra: Optional[Mapping[str, Any]] = None,
    signer: Optional[EphemeralEd25519Signer] = None,
    emitter: Optional[Emitter] = None,
) -> dict[str, Any]:
    """Build, sign, and emit one LedgerProof receipt.

    Parameters
    ----------
    article
        EU AI Act Article 50 sub-article, e.g. ``"50(1)"`` or ``"50(2)"``.
    schema
        Receipt schema name, one of
        ``chatbot_session/v1`` | ``generated_content/v1`` |
        ``on_prem_sovereign_deployment/v1``.
    prompt_text, completion_text
        Hashed locally; never transmitted.
    model
        Model identifier (e.g. ``"luminous-base"`` or ``"luminous-supreme"``).
    extra
        Additional schema-required fields, e.g.
        ``{"hosting_jurisdiction": "DE", "operator": "Acme Bank AG",
        "sovereignty_attestation": "on-prem-frankfurt-dc01"}``.
    """
    schema_cls = schema_for(schema)
    body_kwargs: dict[str, Any] = {
        "article": article,
        "prompt_sha256": sha256_hex(prompt_text),
        "completion_sha256": sha256_hex(completion_text),
        "model": model,
        "model_version": model_version,
        "ts_unix_ms": int(time.time() * 1000),
    }
    if extra:
        body_kwargs.update(extra)

    # chatbot_session/v1 requires session_id_hash — fall back to a stable
    # hash of the prompt if the caller did not supply one.
    if schema == "chatbot_session/v1" and "session_id_hash" not in body_kwargs:
        body_kwargs["session_id_hash"] = sha256_hex(prompt_text)

    body = schema_cls(**body_kwargs)
    payload = body.model_dump(mode="json")

    sgn = signer or _default_signer()
    _, sig = sgn.sign_canonical(payload)

    receipt = {
        "protocol": PROTOCOL_VERSION,
        "payload": payload,
        "sig": base64.b64encode(sig).decode("ascii"),
        "pubkey": sgn.public_key_b64,
    }

    sink = emitter if emitter is not None else _default_emitter()
    sink.emit(receipt)
    return receipt
