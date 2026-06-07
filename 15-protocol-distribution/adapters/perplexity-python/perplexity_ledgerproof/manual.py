"""Manual receipt emission — for users who want explicit control.

```python
import os
from openai import OpenAI
from perplexity_ledgerproof import emit_receipt

client = OpenAI(
    api_key=os.environ["PPLX_API_KEY"],
    base_url="https://api.perplexity.ai",
)
resp = client.chat.completions.create(
    model="sonar",
    messages=[{"role": "user", "content": "Latest news on EU AI Act?"}],
)
emit_receipt(resp, deployer_id="urn:eu:deployer:acme")
```
"""

from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any

from .canonical import canonical_encode, citation_list_hash_hex
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


def extract_citations(response: Any) -> list[str]:
    """Pull citation URLs from a Perplexity response.

    Perplexity Sonar models return citations on the top-level response object
    as `response.citations` (list of URL strings). Some SDK versions or
    response shapes attach them under `model_extra` or as a plain dict — we
    handle both.
    """
    citations: list[str] = []
    # Direct attribute on the response object
    direct = getattr(response, "citations", None)
    if direct:
        citations = [str(c) for c in direct]
    # Pydantic v2 model_extra catch-all
    if not citations:
        extra = getattr(response, "model_extra", None)
        if isinstance(extra, dict) and "citations" in extra:
            citations = [str(c) for c in extra["citations"] or []]
    # Dict-shaped response
    if not citations and isinstance(response, dict) and "citations" in response:
        citations = [str(c) for c in response["citations"] or []]
    return citations


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
    """Build, sign, and emit a receipt for an already-completed Perplexity response.

    Returns the signed envelope dict so callers can also persist / inspect it.
    Does **not** modify `response`.

    For `ai_search_with_citations/v1` and `public_interest_text/v1` schemas,
    the function auto-extracts citation URLs from `response.citations` and
    computes a canonical hash. To override, pass `citations_sha256` and
    `citations_count` through `extra_fields`.

    Use `extra_fields` to inject schema-specific fields like
    `citations_sha256`, `citations_count`, `disclosure_label_shown`,
    `editorial_review`, `subject_category`.
    """
    regulatory_context = regulatory_context or {}
    schema_id = regulatory_context.get("schema", "chatbot_session/v1")

    signer = signer or Ed25519Signer()
    emitter = emitter or LogEmitter()

    model_id = getattr(response, "model", "unknown")
    interaction_id = getattr(response, "id", None) or str(uuid.uuid4())

    base_extra = {"provider": "perplexity"}
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

    # Auto-extract citations for citation-aware schemas (unless overridden).
    citation_schemas = {"ai_search_with_citations/v1", "public_interest_text/v1"}
    if schema_id in citation_schemas:
        if not extra_fields or "citations_sha256" not in extra_fields:
            citations = extract_citations(response)
            auto: dict[str, Any] = {
                "citations_sha256": citation_list_hash_hex(citations),
                "citations_count": len(citations),
            }
            if extra_fields:
                # Preserve deployer-provided keys; only fill what's missing.
                for k, v in auto.items():
                    extra_fields.setdefault(k, v)
            else:
                extra_fields = auto

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
        "adapter": {"name": "ledgerproof-perplexity", "version": __version__},
    }
    emitter.emit(envelope)
    return envelope
