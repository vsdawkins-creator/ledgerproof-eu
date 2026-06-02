"""
Manual receipt emission. Use for full control over when and how a receipt fires,
for example inside a custom orchestration layer or non-standard Anthropic call shape.
"""

from __future__ import annotations

import base64
import uuid
from typing import Any

from .canonical import canonical_encode, hash_text
from .emitter import Emitter, LogEmitter
from .schema import (
    ContentRef,
    ModelRef,
    ReceiptV1,
    RegulatoryContext,
    SchemaName,
    ToolUseRef,
)
from .signer import Ed25519Signer, Signer
from .version import __version__


def _default_regulatory_context() -> RegulatoryContext:
    return RegulatoryContext(
        article_50_paragraph="1",
        deployer_jurisdiction="EU",
        end_user_disclosure_made=True,
    )


def emit_receipt(
    response: Any,
    deployer_id: str,
    regulatory_context: RegulatoryContext | dict[str, Any] | None = None,
    *,
    schema: SchemaName = "chatbot_session/v1",
    signer: Signer | None = None,
    emitter: Emitter | None = None,
    user_message_text: str | None = None,
    streaming: bool = False,
    tool_uses: list[ToolUseRef] | None = None,
) -> dict[str, Any]:
    """
    Build, sign, and emit a receipt for an Anthropic Message response.

    Returns the signed-receipt dict that was emitted (also returned for inspection
    by the caller — never injected into `response`, per constraint C7).
    """
    signer = signer or Ed25519Signer()
    emitter = emitter or LogEmitter()

    if regulatory_context is None:
        regulatory_context = _default_regulatory_context()
    elif isinstance(regulatory_context, dict):
        regulatory_context = RegulatoryContext(**regulatory_context)

    content_refs: list[ContentRef] = []
    if user_message_text:
        content_refs.append(
            ContentRef(
                sha256_hex=hash_text(user_message_text).hex(),
                byte_length=len(user_message_text.encode("utf-8")),
                role="user",
            )
        )

    # Extract assistant text from the Anthropic response.
    assistant_text = _extract_assistant_text(response)
    if assistant_text is not None:
        content_refs.append(
            ContentRef(
                sha256_hex=hash_text(assistant_text).hex(),
                byte_length=len(assistant_text.encode("utf-8")),
                role="assistant",
            )
        )

    # If nothing else, emit a zero-byte assistant ref so the schema invariant holds.
    if not content_refs:
        content_refs.append(
            ContentRef(sha256_hex=hash_text("").hex(), byte_length=0, role="assistant")
        )

    model_ref = _build_model_ref(response)

    receipt = ReceiptV1(
        schema=schema,
        receipt_id=str(uuid.uuid4()),
        deployer_id=deployer_id,
        model=model_ref,
        content_refs=content_refs,
        regulatory_context=regulatory_context,
        tool_uses=tool_uses or [],
        streaming=streaming,
        adapter_version=__version__,
    )

    payload = receipt.to_payload()
    canonical_bytes = canonical_encode(payload)
    signature = signer.sign(canonical_bytes)

    signed = {
        "receipt": payload,
        "signature_alg": "ed25519",
        "signature_b64": base64.b64encode(signature).decode("ascii"),
        "signer_key_id": signer.key_id,
        "canonical_encoding": "cbor-rfc8949-deterministic",
    }
    emitter.emit(signed)
    return signed


def _extract_assistant_text(response: Any) -> str | None:
    """Pull plain text out of an Anthropic Message response, defensively."""
    if response is None:
        return None
    content = getattr(response, "content", None)
    if content is None:
        return None
    chunks: list[str] = []
    for block in content:
        text = getattr(block, "text", None)
        if isinstance(text, str):
            chunks.append(text)
    return "".join(chunks) if chunks else None


def _build_model_ref(response: Any) -> ModelRef:
    response_id = getattr(response, "id", None) or "unknown"
    model_id = getattr(response, "model", None) or "unknown"
    stop_reason = getattr(response, "stop_reason", None)
    usage = getattr(response, "usage", None)
    input_tokens = getattr(usage, "input_tokens", None) if usage is not None else None
    output_tokens = getattr(usage, "output_tokens", None) if usage is not None else None
    return ModelRef(
        model_id=str(model_id),
        response_id=str(response_id),
        stop_reason=str(stop_reason) if stop_reason else None,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )


def extract_tool_uses(response: Any) -> list[ToolUseRef]:
    """Inspect an Anthropic response for ToolUseBlock entries and hash them."""
    refs: list[ToolUseRef] = []
    content = getattr(response, "content", None) or []
    for block in content:
        block_type = getattr(block, "type", None)
        if block_type != "tool_use":
            continue
        tool_name = getattr(block, "name", None) or "unknown"
        tool_use_id = getattr(block, "id", None) or "unknown"
        tool_input = getattr(block, "input", None) or {}
        try:
            input_bytes = canonical_encode(tool_input) if isinstance(tool_input, dict) else str(tool_input).encode()
        except Exception:
            input_bytes = repr(tool_input).encode("utf-8")
        import hashlib

        refs.append(
            ToolUseRef(
                tool_name=str(tool_name)[:128],
                tool_use_id=str(tool_use_id)[:128],
                input_sha256_hex=hashlib.sha256(input_bytes).hexdigest(),
            )
        )
    return refs
