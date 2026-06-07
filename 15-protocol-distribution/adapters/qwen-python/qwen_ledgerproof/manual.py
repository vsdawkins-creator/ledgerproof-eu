"""
Manual receipt emission. Use for full control over when and how a receipt fires,
for example inside a custom orchestration layer or non-standard Qwen call shape.
"""

from __future__ import annotations

import base64
import hashlib
import json
import uuid
from typing import Any

from .canonical import canonical_encode, hash_text
from .emitter import Emitter, LogEmitter
from .schema import (
    ChineseInferenceAttestation,
    ContentRef,
    CrossJurisdictionalRoute,
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
    user_session_id: str | None = None,
    chinese_inference: ChineseInferenceAttestation | dict[str, Any] | None = None,
    cross_jurisdictional_route: CrossJurisdictionalRoute | dict[str, Any] | None = None,
    model_id: str | None = None,
) -> dict[str, Any]:
    """
    Build, sign, and emit a receipt for a DashScope GenerationResponse.

    Returns the signed-receipt dict that was emitted (also returned for inspection
    by the caller — never injected into `response`, per constraint C7).
    """
    signer = signer or Ed25519Signer()
    emitter = emitter or LogEmitter()

    if regulatory_context is None:
        regulatory_context = _default_regulatory_context()
    elif isinstance(regulatory_context, dict):
        regulatory_context = RegulatoryContext(**regulatory_context)

    if isinstance(chinese_inference, dict):
        chinese_inference = ChineseInferenceAttestation(**chinese_inference)
    if isinstance(cross_jurisdictional_route, dict):
        cross_jurisdictional_route = CrossJurisdictionalRoute(**cross_jurisdictional_route)

    content_refs: list[ContentRef] = []
    if user_message_text:
        content_refs.append(
            ContentRef(
                sha256_hex=hash_text(user_message_text).hex(),
                byte_length=len(user_message_text.encode("utf-8")),
                role="user",
            )
        )

    assistant_text = _extract_assistant_text(response)
    if assistant_text is not None:
        content_refs.append(
            ContentRef(
                sha256_hex=hash_text(assistant_text).hex(),
                byte_length=len(assistant_text.encode("utf-8")),
                role="assistant",
            )
        )

    # Schema invariant: at least one content_ref must be present.
    if not content_refs:
        content_refs.append(
            ContentRef(sha256_hex=hash_text("").hex(), byte_length=0, role="assistant")
        )

    model_ref = _build_model_ref(response, fallback_model_id=model_id)

    receipt = ReceiptV1(
        schema=schema,
        receipt_id=str(uuid.uuid4()),
        deployer_id=deployer_id,
        user_session_id=user_session_id,
        model=model_ref,
        content_refs=content_refs,
        regulatory_context=regulatory_context,
        chinese_inference=chinese_inference,
        cross_jurisdictional_route=cross_jurisdictional_route,
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
    """
    Pull plain text out of a DashScope GenerationResponse, defensively.

    DashScope `Generation.call` returns a GenerationResponse with shape:

        response.output.text                              -> str  (message mode default)
        response.output.choices[0].message.content        -> str  (chat-message mode)
        response.output["text"] / response.output["choices"][0]["message"]["content"]
            (dict-style indexing also supported)
    """
    if response is None:
        return None
    output = getattr(response, "output", None)
    if output is None and isinstance(response, dict):
        output = response.get("output")
    if output is None:
        return None

    # Plain-text mode: output.text
    text = getattr(output, "text", None)
    if text is None and isinstance(output, dict):
        text = output.get("text")
    if isinstance(text, str) and text:
        return text

    # Chat-message mode: output.choices[0].message.content
    choices = getattr(output, "choices", None)
    if choices is None and isinstance(output, dict):
        choices = output.get("choices")
    if not choices:
        return None
    first = choices[0]
    message = getattr(first, "message", None)
    if message is None and isinstance(first, dict):
        message = first.get("message")
    if message is None:
        return None
    content = getattr(message, "content", None)
    if content is None and isinstance(message, dict):
        content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        # MultiModal responses may return a list of content blocks; pull text out.
        parts: list[str] = []
        for chunk in content:
            text = getattr(chunk, "text", None)
            if text is None and isinstance(chunk, dict):
                text = chunk.get("text")
            if isinstance(text, str):
                parts.append(text)
        return "".join(parts) if parts else None
    return None


def _build_model_ref(response: Any, fallback_model_id: str | None = None) -> ModelRef:
    if response is None:
        return ModelRef(
            model_id=fallback_model_id or "unknown",
            response_id="unknown",
        )

    # DashScope canonical fields
    response_id = (
        getattr(response, "request_id", None)
        or (response.get("request_id") if isinstance(response, dict) else None)
        or "unknown"
    )

    # DashScope does NOT echo back the model id on most response shapes; the
    # caller-provided fallback is the primary source.
    model_id = fallback_model_id or "unknown"

    # Finish reason: output.finish_reason or output.choices[0].finish_reason
    finish_reason: str | None = None
    output = getattr(response, "output", None)
    if output is None and isinstance(response, dict):
        output = response.get("output")
    if output is not None:
        finish_reason = getattr(output, "finish_reason", None)
        if finish_reason is None and isinstance(output, dict):
            finish_reason = output.get("finish_reason")
        if finish_reason is None:
            choices = getattr(output, "choices", None) or (
                output.get("choices") if isinstance(output, dict) else None
            )
            if choices:
                first = choices[0]
                finish_reason = getattr(first, "finish_reason", None)
                if finish_reason is None and isinstance(first, dict):
                    finish_reason = first.get("finish_reason")

    # Usage block: response.usage.input_tokens / output_tokens / total_tokens
    usage = getattr(response, "usage", None)
    if usage is None and isinstance(response, dict):
        usage = response.get("usage")
    prompt_tokens = completion_tokens = total_tokens = None
    if usage is not None:
        prompt_tokens = getattr(usage, "input_tokens", None)
        if prompt_tokens is None and isinstance(usage, dict):
            prompt_tokens = usage.get("input_tokens")
        completion_tokens = getattr(usage, "output_tokens", None)
        if completion_tokens is None and isinstance(usage, dict):
            completion_tokens = usage.get("output_tokens")
        total_tokens = getattr(usage, "total_tokens", None)
        if total_tokens is None and isinstance(usage, dict):
            total_tokens = usage.get("total_tokens")

    return ModelRef(
        model_id=str(model_id),
        response_id=str(response_id),
        finish_reason=str(finish_reason) if finish_reason else None,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
    )


def extract_tool_uses(response: Any) -> list[ToolUseRef]:
    """
    Inspect a DashScope GenerationResponse for tool/function calls and hash them.

    DashScope shape:
        response.output.choices[0].message.tool_calls -> list of
            {"id": ..., "type": "function", "function": {"name": ..., "arguments": ...}}
    """
    refs: list[ToolUseRef] = []
    output = getattr(response, "output", None)
    if output is None and isinstance(response, dict):
        output = response.get("output")
    if output is None:
        return refs
    choices = getattr(output, "choices", None)
    if choices is None and isinstance(output, dict):
        choices = output.get("choices")
    if not choices:
        return refs
    message = getattr(choices[0], "message", None)
    if message is None and isinstance(choices[0], dict):
        message = choices[0].get("message")
    if message is None:
        return refs
    tool_calls = getattr(message, "tool_calls", None)
    if tool_calls is None and isinstance(message, dict):
        tool_calls = message.get("tool_calls")
    if not tool_calls:
        return refs

    for call in tool_calls:
        tool_use_id = (
            getattr(call, "id", None)
            or (call.get("id") if isinstance(call, dict) else None)
            or "unknown"
        )
        function = getattr(call, "function", None)
        if function is None and isinstance(call, dict):
            function = call.get("function")
        tool_name = "unknown"
        arguments: Any = None
        if function is not None:
            tool_name = (
                getattr(function, "name", None)
                or (function.get("name") if isinstance(function, dict) else None)
                or "unknown"
            )
            arguments = getattr(function, "arguments", None)
            if arguments is None and isinstance(function, dict):
                arguments = function.get("arguments")

        # Arguments may already be a JSON string in DashScope SDK; normalise.
        if isinstance(arguments, str):
            try:
                arguments_obj = json.loads(arguments)
                input_bytes = (
                    canonical_encode(arguments_obj)
                    if isinstance(arguments_obj, dict)
                    else arguments.encode("utf-8")
                )
            except json.JSONDecodeError:
                input_bytes = arguments.encode("utf-8")
        elif isinstance(arguments, dict):
            input_bytes = canonical_encode(arguments)
        elif arguments is None:
            input_bytes = b""
        else:
            input_bytes = repr(arguments).encode("utf-8")

        refs.append(
            ToolUseRef(
                tool_name=str(tool_name)[:128],
                tool_use_id=str(tool_use_id)[:128],
                input_sha256_hex=hashlib.sha256(input_bytes).hexdigest(),
            )
        )
    return refs
