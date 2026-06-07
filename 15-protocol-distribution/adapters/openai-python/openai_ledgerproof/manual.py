"""Manual receipt emission — for users who want explicit control.

```python
from openai import OpenAI
from openai_ledgerproof import emit_receipt

client = OpenAI()
resp = client.chat.completions.create(...)
emit_receipt(resp, deployer_id="urn:eu:deployer:acme")
```
"""

from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any

from .canonical import canonical_encode
from .emitter import Emitter, LogEmitter
from .schema import build_receipt
from .signer import Ed25519Signer, Signer
from .version import __version__


def _hash_messages(messages: list[dict[str, Any]] | None) -> str:
    if not messages:
        return hashlib.sha256(b"").hexdigest()
    payload = json.dumps(messages, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _hash_response_text(response: Any) -> str:
    """SHA-256 over the concatenated assistant text from all choices."""
    parts: list[str] = []
    choices = getattr(response, "choices", None) or []
    for choice in choices:
        msg = getattr(choice, "message", None)
        if msg is None:
            continue
        content = getattr(msg, "content", None)
        if content:
            parts.append(content)
    return hashlib.sha256("".join(parts).encode("utf-8")).hexdigest()


def emit_receipt(
    response: Any,
    deployer_id: str,
    *,
    messages: list[dict[str, Any]] | None = None,
    regulatory_context: dict[str, Any] | None = None,
    signer: Signer | None = None,
    emitter: Emitter | None = None,
    user_pseudonym: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build, sign, and emit a receipt for an already-completed OpenAI response.

    Returns the signed envelope dict so callers can also persist / inspect it.
    Does **not** modify `response`.
    """
    regulatory_context = regulatory_context or {}
    schema_id = regulatory_context.get("schema", "chatbot_session/v1")

    signer = signer or Ed25519Signer()
    emitter = emitter or LogEmitter()

    model_id = getattr(response, "model", "unknown")
    interaction_id = getattr(response, "id", None) or str(uuid.uuid4())

    receipt = build_receipt(
        schema_id,
        deployer_id=deployer_id,
        model_id=model_id,
        interaction_id=interaction_id,
        prompt_sha256=_hash_messages(messages),
        response_sha256=_hash_response_text(response),
        user_pseudonym=user_pseudonym,
        jurisdiction=regulatory_context.get("jurisdiction", "EU"),
        extra=extra or {},
    )

    receipt_dict = receipt.model_dump()
    canonical_bytes = canonical_encode(receipt_dict)
    signature = signer.sign(canonical_bytes)

    envelope = {
        "receipt": receipt_dict,
        "signature": signature.hex(),
        "signature_alg": "ed25519",
        "public_key": signer.public_key_bytes().hex(),
        "adapter": {"name": "ledgerproof-openai", "version": __version__},
    }
    emitter.emit(envelope)
    return envelope
