"""Manual receipt emission — for users who want explicit control.

```python
import os
from openai import OpenAI
from deepseek_ledgerproof import emit_receipt

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)
resp = client.chat.completions.create(
    model="deepseek-chat",
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


def _extract_answer_and_reasoning(response: Any) -> tuple[str, str]:
    """Concatenated assistant text + reasoning trace across all choices."""
    answer_parts: list[str] = []
    reasoning_parts: list[str] = []
    for choice in getattr(response, "choices", None) or []:
        msg = getattr(choice, "message", None)
        if msg is None:
            continue
        content = getattr(msg, "content", None)
        if content:
            answer_parts.append(content)
        reasoning = getattr(msg, "reasoning_content", None)
        if reasoning:
            reasoning_parts.append(reasoning)
    return "".join(answer_parts), "".join(reasoning_parts)


def emit_receipt(
    response: Any,
    deployer_id: str,
    *,
    messages: list[dict[str, Any]] | None = None,
    regulatory_context: dict[str, Any] | None = None,
    signer: Signer | None = None,
    emitter: Emitter | None = None,
    user_pseudonym: str | None = None,
    session_id: str | None = None,
    extra: dict[str, Any] | None = None,
    extra_fields: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build, sign, and emit a receipt for an already-completed DeepSeek response.

    Returns the signed envelope dict so callers can also persist / inspect it.
    Does **not** modify `response`.

    Use `extra_fields` to inject schema-specific fields like `reasoning_sha256`,
    `trace_surfaced_to_user`, `programming_language`.
    """
    regulatory_context = regulatory_context or {}
    schema_id = regulatory_context.get("schema", "chatbot_session/v1")

    signer = signer or Ed25519Signer()
    emitter = emitter or LogEmitter()

    model_id = getattr(response, "model", "unknown")
    interaction_id = getattr(response, "id", None) or str(uuid.uuid4())

    answer_text, reasoning_text = _extract_answer_and_reasoning(response)

    base_extra = {"provider": "deepseek"}
    if extra:
        base_extra.update(extra)

    # Auto-populate reasoning fields when schema is reasoning_trace/v1 and we
    # found a trace; deployer-supplied extra_fields wins.
    auto_extra: dict[str, Any] = {}
    if schema_id == "reasoning_trace/v1" and reasoning_text:
        auto_extra["reasoning_sha256"] = hashlib.sha256(
            reasoning_text.encode("utf-8")
        ).hexdigest()

    kwargs: dict[str, Any] = dict(
        deployer_id=deployer_id,
        model_id=model_id,
        interaction_id=interaction_id,
        prompt_sha256=_hash_messages(messages),
        response_sha256=hashlib.sha256(answer_text.encode("utf-8")).hexdigest(),
        user_pseudonym=user_pseudonym or regulatory_context.get("user_pseudonym"),
        session_id=session_id or regulatory_context.get("session_id"),
        jurisdiction=regulatory_context.get("jurisdiction", "EU"),
        extra=base_extra,
    )
    kwargs.update(auto_extra)
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
        "adapter": {"name": "ledgerproof-deepseek", "version": __version__},
    }
    try:
        emitter.emit(envelope)
    except Exception:  # noqa: BLE001
        # C7 — emission failure must never raise into the caller path.
        pass
    return envelope
