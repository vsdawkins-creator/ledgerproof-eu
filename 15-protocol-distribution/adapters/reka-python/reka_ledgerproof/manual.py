"""
Manual receipt emission. Use for full control over when and how a receipt fires,
for example inside a custom orchestration layer or non-standard Reka call shape.
"""

from __future__ import annotations

import base64
import hashlib
import uuid
from typing import Any, Iterable

from .canonical import canonical_encode, hash_text
from .emitter import Emitter, LogEmitter
from .schema import (
    ContentRef,
    MediaRef,
    Modality,
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
    media_refs: Iterable[MediaRef] | None = None,
    input_modalities: list[Modality] | None = None,
) -> dict[str, Any]:
    """
    Build, sign, and emit a receipt for a Reka chat response.

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
                modality="text",
            )
        )

    assistant_text = _extract_assistant_text(response)
    if assistant_text is not None:
        content_refs.append(
            ContentRef(
                sha256_hex=hash_text(assistant_text).hex(),
                byte_length=len(assistant_text.encode("utf-8")),
                role="assistant",
                modality="text",
            )
        )

    if not content_refs:
        content_refs.append(
            ContentRef(
                sha256_hex=hash_text("").hex(),
                byte_length=0,
                role="assistant",
                modality="text",
            )
        )

    model_ref = _build_model_ref(response)

    media_list = list(media_refs) if media_refs is not None else []
    modalities = input_modalities or _derive_modalities(content_refs, media_list)

    receipt = ReceiptV1(
        schema=schema,
        receipt_id=str(uuid.uuid4()),
        deployer_id=deployer_id,
        model=model_ref,
        content_refs=content_refs,
        media_refs=media_list,
        regulatory_context=regulatory_context,
        tool_uses=tool_uses or [],
        input_modalities=modalities,
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


def _derive_modalities(
    content_refs: list[ContentRef], media_refs: list[MediaRef]
) -> list[Modality]:
    seen: list[Modality] = []
    for c in content_refs:
        if c.role == "user" and c.modality not in seen:
            seen.append(c.modality)
    for m in media_refs:
        if m.modality not in seen:
            seen.append(m.modality)
    return seen or ["text"]


def _extract_assistant_text(response: Any) -> str | None:
    """
    Pull plain text out of a Reka ChatResponse, defensively.

    Reka's `ChatResponse` exposes the assistant message under
    `responses[0].message.content` (per the Reka Python SDK). We probe a couple
    of attribute paths so this keeps working across minor SDK revisions.
    """
    if response is None:
        return None

    # Reka v3.x: response.responses[i].message.content
    responses = getattr(response, "responses", None)
    if responses:
        try:
            first = responses[0]
            message = getattr(first, "message", None)
            content = getattr(message, "content", None) if message is not None else None
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                parts: list[str] = []
                for block in content:
                    text = getattr(block, "text", None)
                    if isinstance(text, str):
                        parts.append(text)
                    elif isinstance(block, dict) and isinstance(block.get("text"), str):
                        parts.append(block["text"])
                if parts:
                    return "".join(parts)
        except (IndexError, AttributeError):
            pass

    # Fallbacks for other SDK shapes.
    direct = getattr(response, "content", None)
    if isinstance(direct, str):
        return direct
    text_attr = getattr(response, "text", None)
    if isinstance(text_attr, str):
        return text_attr
    return None


def _build_model_ref(response: Any) -> ModelRef:
    response_id = getattr(response, "id", None) or "unknown"
    model_id = getattr(response, "model", None) or "unknown"
    finish_reason = getattr(response, "finish_reason", None)
    # Reka also exposes `responses[0].finish_reason` in some versions.
    if finish_reason is None:
        responses = getattr(response, "responses", None)
        if responses:
            try:
                finish_reason = getattr(responses[0], "finish_reason", None)
            except (IndexError, AttributeError):
                finish_reason = None
    usage = getattr(response, "usage", None)
    input_tokens = getattr(usage, "input_tokens", None) if usage is not None else None
    output_tokens = getattr(usage, "output_tokens", None) if usage is not None else None
    return ModelRef(
        model_id=str(model_id),
        response_id=str(response_id),
        finish_reason=str(finish_reason) if finish_reason else None,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )


def extract_tool_uses(response: Any) -> list[ToolUseRef]:
    """Inspect a Reka response for tool_calls entries and hash them."""
    refs: list[ToolUseRef] = []
    tool_calls = _find_tool_calls(response)
    for call in tool_calls:
        tool_name = (
            getattr(call, "name", None)
            or (call.get("name") if isinstance(call, dict) else None)
            or "unknown"
        )
        tool_use_id = (
            getattr(call, "id", None)
            or (call.get("id") if isinstance(call, dict) else None)
            or "unknown"
        )
        tool_input = (
            getattr(call, "arguments", None)
            or getattr(call, "input", None)
            or (call.get("arguments") if isinstance(call, dict) else None)
            or {}
        )
        try:
            if isinstance(tool_input, dict):
                input_bytes = canonical_encode(tool_input)
            elif isinstance(tool_input, str):
                input_bytes = tool_input.encode("utf-8")
            else:
                input_bytes = repr(tool_input).encode("utf-8")
        except Exception:
            input_bytes = repr(tool_input).encode("utf-8")

        refs.append(
            ToolUseRef(
                tool_name=str(tool_name)[:128],
                tool_use_id=str(tool_use_id)[:128],
                input_sha256_hex=hashlib.sha256(input_bytes).hexdigest(),
            )
        )
    return refs


def _find_tool_calls(response: Any) -> list[Any]:
    """Locate tool_calls across plausible Reka response shapes."""
    if response is None:
        return []
    direct = getattr(response, "tool_calls", None)
    if direct:
        return list(direct)
    responses = getattr(response, "responses", None)
    if responses:
        try:
            first = responses[0]
            calls = getattr(first, "tool_calls", None)
            if calls:
                return list(calls)
            message = getattr(first, "message", None)
            if message is not None:
                calls = getattr(message, "tool_calls", None)
                if calls:
                    return list(calls)
        except (IndexError, AttributeError):
            return []
    return []
