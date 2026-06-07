"""Manual receipt emission — for users who want explicit control.

```python
import os
from openai import OpenAI
from xai_ledgerproof import emit_receipt

client = OpenAI(
    api_key=os.environ["XAI_API_KEY"],
    base_url="https://api.x.ai/v1",
)
resp = client.chat.completions.create(
    model="grok-2-latest",
    messages=[{"role": "user", "content": "hello"}],
)
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
    extra_fields: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build, sign, and emit a receipt for an already-completed xAI Grok response.

    Returns the signed envelope dict so callers can also persist / inspect it.
    Does **not** modify `response`.

    Use `extra_fields` to inject schema-specific fields like
    `realtime_sources_sha256`, `realtime_data_used`, `public_interest_text`,
    `image_input_sha256`, `image_count`.
    """
    regulatory_context = regulatory_context or {}
    schema_id = regulatory_context.get("schema", "chatbot_session/v1")

    signer = signer or Ed25519Signer()
    emitter = emitter or LogEmitter()

    model_id = getattr(response, "model", "unknown")
    interaction_id = getattr(response, "id", None) or str(uuid.uuid4())

    base_extra = {"provider": "xai"}
    if extra:
        base_extra.update(extra)

    kwargs: dict[str, Any] = dict(
        deployer_id=deployer_id,
        model_id=model_id,
        interaction_id=interaction_id,
        prompt_sha256=_hash_messages(messages),
        response_sha256=_hash_response_text(response),
        user_pseudonym=user_pseudonym,
        jurisdiction=regulatory_context.get("jurisdiction", "EU"),
        extra=base_extra,
    )
    if extra_fields:
        kwargs.update(extra_fields)

    receipt = build_receipt(schema_id, **kwargs)

    receipt_dict = receipt.model_dump()
    canonical_bytes = canonical_encode(receipt_dict)
    signature = signer.sign(canonical_bytes)

    envelope = {
        "receipt": receipt_dict,
        "signature": signature.hex(),
        "signature_alg": "ed25519",
        "public_key": signer.public_key_bytes().hex(),
        "adapter": {"name": "ledgerproof-xai", "version": __version__},
    }
    emitter.emit(envelope)
    return envelope
