"""
Manual receipt emission for AI21 chat completions.

Use when you want full control over when/how a receipt fires — e.g. inside
custom orchestration, multi-turn pipelines, or non-standard call shapes.
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
    ContentRef,
    JambaHybridAttestation,
    LongContextAttestation,
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
    long_context: LongContextAttestation | dict[str, Any] | None = None,
    jamba_hybrid: JambaHybridAttestation | dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Build, sign, and emit a receipt for an AI21 ChatCompletionResponse.

    Returns the signed-receipt dict that was emitted (also returned for inspection
    by the caller — never injected into `response`, per constraint C7).
    """
    signer = signer or Ed25519Signer()
    emitter = emitter or LogEmitter()

    if regulatory_context is None:
        regulatory_context = _default_regulatory_context()
    elif isinstance(regulatory_context, dict):
        regulatory_context = RegulatoryContext(**regulatory_context)

    if isinstance(long_context, dict):
        long_context = LongContextAttestation(**long_context)
    if isinstance(jamba_hybrid, dict):
        jamba_hybrid = JambaHybridAttestation(**jamba_hybrid)

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

    model_ref = _build_model_ref(response)

    receipt = ReceiptV1(
        schema=schema,
        receipt_id=str(uuid.uuid4()),
        deployer_id=deployer_id,
        user_session_id=user_session_id,
        model=model_ref,
        content_refs=content_refs,
        regulatory_context=regulatory_context,
        long_context=long_context,
        jamba_hybrid=jamba_hybrid,
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
    Pull plain text out of an AI21 ChatCompletionResponse, defensively.

    AI21 SDK (ai21>=3.0) returns an OpenAI-compatible shape:
        response.choices[0].message.content  -> str
    """
    if response is None:
        return None
    choices = getattr(response, "choices", None)
    if not choices:
        return None
    first = choices[0]
    message = getattr(first, "message", None)
    if message is None:
        if isinstance(first, dict):
            message = first.get("message")
        if message is None:
            return None
    content = getattr(message, "content", None)
    if content is None and isinstance(message, dict):
        content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        # Defensive: AI21 may evolve toward multimodal content lists.
        parts: list[str] = []
        for chunk in content:
            text = getattr(chunk, "text", None)
            if text is None and isinstance(chunk, dict):
                text = chunk.get("text")
            if isinstance(text, str):
                parts.append(text)
        return "".join(parts) if parts else None
    return None


def _build_model_ref(response: Any) -> ModelRef:
    if response is None:
        return ModelRef(model_id="unknown", response_id="unknown")
    response_id = getattr(response, "id", None) or "unknown"
    model_id = getattr(response, "model", None) or "unknown"

    finish_reason: str | None = None
    choices = getattr(response, "choices", None) or []
    if choices:
        finish_reason = getattr(choices[0], "finish_reason", None)
        if finish_reason is None and isinstance(choices[0], dict):
            finish_reason = choices[0].get("finish_reason")

    usage = getattr(response, "usage", None)
    prompt_tokens = getattr(usage, "prompt_tokens", None) if usage is not None else None
    completion_tokens = getattr(usage, "completion_tokens", None) if usage is not None else None
    total_tokens = getattr(usage, "total_tokens", None) if usage is not None else None

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
    Inspect an AI21 ChatCompletionResponse for function/tool calls and hash them.

    AI21 follows the OpenAI tool-call shape:
        response.choices[0].message.tool_calls -> list of
            ToolCall(id=..., function=FunctionCall(name=..., arguments=...))
    """
    refs: list[ToolUseRef] = []
    choices = getattr(response, "choices", None) or []
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

        # Arguments are usually a JSON string in OpenAI-compatible SDKs.
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
