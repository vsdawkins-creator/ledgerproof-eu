"""
Manual receipt emission. Use for full control over when and how a receipt fires,
for example inside a custom orchestration layer, an image-generation pipeline,
or a non-standard Together call shape.
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
    ModelRef,
    OpenModelAttribution,
    ReceiptV1,
    RegulatoryContext,
    SchemaName,
    ToolUseRef,
    infer_open_model_attribution,
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
    open_model: OpenModelAttribution | dict[str, Any] | None = None,
    extra_content_refs: list[ContentRef] | None = None,
) -> dict[str, Any]:
    """
    Build, sign, and emit a receipt for a Together ChatCompletionResponse
    (or any OpenAI-compatible response shape Together returns).

    Returns the signed-receipt dict that was emitted (also returned for inspection
    by the caller — never injected into `response`, per constraint C7).
    """
    signer = signer or Ed25519Signer()
    emitter = emitter or LogEmitter()

    if regulatory_context is None:
        regulatory_context = _default_regulatory_context()
    elif isinstance(regulatory_context, dict):
        regulatory_context = RegulatoryContext(**regulatory_context)

    if isinstance(open_model, dict):
        open_model = OpenModelAttribution(**open_model)

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

    if extra_content_refs:
        content_refs.extend(extra_content_refs)

    # Schema invariant: at least one content_ref must be present.
    if not content_refs:
        content_refs.append(
            ContentRef(sha256_hex=hash_text("").hex(), byte_length=0, role="assistant")
        )

    model_ref = _build_model_ref(response)

    # If the deployer chose open_model_inference/v1 without supplying explicit
    # attribution, attempt best-effort inference from the model id.
    if schema == "open_model_inference/v1" and open_model is None:
        open_model = infer_open_model_attribution(model_ref.model_id)

    receipt = ReceiptV1(
        schema=schema,
        receipt_id=str(uuid.uuid4()),
        deployer_id=deployer_id,
        user_session_id=user_session_id,
        model=model_ref,
        content_refs=content_refs,
        regulatory_context=regulatory_context,
        open_model=open_model,
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
    Pull plain text out of a Together ChatCompletionResponse, defensively.

    Together returns OpenAI-compatible shape:
        response.choices[0].message.content  -> str or list[ContentBlock]
    """
    if response is None:
        return None
    choices = getattr(response, "choices", None)
    if not choices and isinstance(response, dict):
        choices = response.get("choices")
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
    response_id = getattr(response, "id", None)
    if response_id is None and isinstance(response, dict):
        response_id = response.get("id")
    model_id = getattr(response, "model", None)
    if model_id is None and isinstance(response, dict):
        model_id = response.get("model")
    response_id = response_id or "unknown"
    model_id = model_id or "unknown"

    finish_reason: str | None = None
    choices = getattr(response, "choices", None)
    if choices is None and isinstance(response, dict):
        choices = response.get("choices")
    choices = choices or []
    if choices:
        finish_reason = getattr(choices[0], "finish_reason", None)
        if finish_reason is None and isinstance(choices[0], dict):
            finish_reason = choices[0].get("finish_reason")

    usage = getattr(response, "usage", None)
    if usage is None and isinstance(response, dict):
        usage = response.get("usage")
    prompt_tokens = None
    completion_tokens = None
    total_tokens = None
    if usage is not None:
        prompt_tokens = getattr(usage, "prompt_tokens", None)
        completion_tokens = getattr(usage, "completion_tokens", None)
        total_tokens = getattr(usage, "total_tokens", None)
        if isinstance(usage, dict):
            prompt_tokens = prompt_tokens if prompt_tokens is not None else usage.get("prompt_tokens")
            completion_tokens = completion_tokens if completion_tokens is not None else usage.get("completion_tokens")
            total_tokens = total_tokens if total_tokens is not None else usage.get("total_tokens")

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
    Inspect a Together ChatCompletionResponse for function/tool calls and hash them.

    Together (OpenAI-compatible) shape:
        response.choices[0].message.tool_calls -> list of
            ToolCall(id=..., function=FunctionCall(name=..., arguments=...))
    """
    refs: list[ToolUseRef] = []
    choices = getattr(response, "choices", None)
    if choices is None and isinstance(response, dict):
        choices = response.get("choices")
    choices = choices or []
    if not choices:
        return refs
    first = choices[0]
    message = getattr(first, "message", None)
    if message is None and isinstance(first, dict):
        message = first.get("message")
    if message is None:
        return refs
    tool_calls = getattr(message, "tool_calls", None)
    if tool_calls is None and isinstance(message, dict):
        tool_calls = message.get("tool_calls")
    if not tool_calls:
        return refs

    for call in tool_calls:
        tool_use_id = getattr(call, "id", None) or (
            call.get("id") if isinstance(call, dict) else None
        ) or "unknown"
        function = getattr(call, "function", None)
        if function is None and isinstance(call, dict):
            function = call.get("function")
        tool_name = "unknown"
        arguments: Any = None
        if function is not None:
            tool_name = getattr(function, "name", None) or (
                function.get("name") if isinstance(function, dict) else None
            ) or "unknown"
            arguments = getattr(function, "arguments", None)
            if arguments is None and isinstance(function, dict):
                arguments = function.get("arguments")

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


# ---------------------------------------------------------------------------
# Image-generation helpers (FLUX & friends)
# ---------------------------------------------------------------------------


def emit_image_generation_receipt(
    response: Any,
    deployer_id: str,
    *,
    prompt_text: str,
    image_bytes_iter: list[bytes] | None = None,
    image_sha256_hexes: list[str] | None = None,
    signer: Signer | None = None,
    emitter: Emitter | None = None,
    open_model: OpenModelAttribution | dict[str, Any] | None = None,
    regulatory_context: RegulatoryContext | dict[str, Any] | None = None,
    user_session_id: str | None = None,
) -> dict[str, Any]:
    """
    Emit an image_generation/v1 receipt for Together image endpoints (e.g. FLUX).

    Pass either:
      - `image_bytes_iter`: raw bytes per image (we hash them), OR
      - `image_sha256_hexes`: pre-computed hex digests of each image.

    Together's image endpoint returns a list of image URLs or base64 strings;
    the caller decides how to materialise bytes to hash.
    """
    signer = signer or Ed25519Signer()
    emitter = emitter or LogEmitter()

    if regulatory_context is None:
        regulatory_context = RegulatoryContext(
            article_50_paragraph="2",  # generated content
            deployer_jurisdiction="EU",
            end_user_disclosure_made=True,
        )
    elif isinstance(regulatory_context, dict):
        regulatory_context = RegulatoryContext(**regulatory_context)

    if isinstance(open_model, dict):
        open_model = OpenModelAttribution(**open_model)

    model_ref = _build_model_ref(response)

    # User-prompt hash (Article 50(2) wants synthetic-content provenance).
    content_refs: list[ContentRef] = [
        ContentRef(
            sha256_hex=hash_text(prompt_text).hex(),
            byte_length=len(prompt_text.encode("utf-8")),
            role="user",
        )
    ]
    # Image content hashes
    if image_bytes_iter:
        for blob in image_bytes_iter:
            content_refs.append(
                ContentRef(
                    sha256_hex=hashlib.sha256(blob).hexdigest(),
                    byte_length=len(blob),
                    role="image",
                )
            )
    if image_sha256_hexes:
        for hex_digest in image_sha256_hexes:
            content_refs.append(
                ContentRef(
                    sha256_hex=hex_digest,
                    byte_length=0,
                    role="image",
                )
            )

    # Best-effort attribution from model_id if not supplied
    if open_model is None:
        open_model = infer_open_model_attribution(model_ref.model_id)

    receipt = ReceiptV1(
        schema="image_generation/v1",
        receipt_id=str(uuid.uuid4()),
        deployer_id=deployer_id,
        user_session_id=user_session_id,
        model=model_ref,
        content_refs=content_refs,
        regulatory_context=regulatory_context,
        open_model=open_model,
        streaming=False,
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
