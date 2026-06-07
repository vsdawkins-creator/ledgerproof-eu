"""
Manual receipt emission for Codestral. Use for full control over when and how a
receipt fires — especially for safety_critical_code_review/v1 which requires
deployer-asserted review metadata not present in any Codestral response.
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
    FimPositions,
    GeneratedCodeAttributes,
    ModelRef,
    ReceiptV1,
    RegulatoryContext,
    SafetyCriticalReview,
    SchemaName,
    ToolUseRef,
)
from .signer import Ed25519Signer, Signer
from .version import __version__


def _default_regulatory_context() -> RegulatoryContext:
    return RegulatoryContext(
        article_50_paragraph="2",  # Codestral default = generated content
        deployer_jurisdiction="EU",
        end_user_disclosure_made=True,
    )


def emit_receipt(
    response: Any,
    deployer_id: str,
    regulatory_context: RegulatoryContext | dict[str, Any] | None = None,
    *,
    schema: SchemaName = "generated_code/v1",
    signer: Signer | None = None,
    emitter: Emitter | None = None,
    user_message_text: str | None = None,
    streaming: bool = False,
    tool_uses: list[ToolUseRef] | None = None,
    user_session_id: str | None = None,
    code_attributes: GeneratedCodeAttributes | dict[str, Any] | None = None,
    fim_positions: FimPositions | dict[str, Any] | None = None,
    safety_review: SafetyCriticalReview | dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Build, sign, and emit a receipt for a Codestral response.

    Returns the signed-receipt dict that was emitted (also returned for inspection
    by the caller — never injected into `response`, per constraint C7).
    """
    signer = signer or Ed25519Signer()
    emitter = emitter or LogEmitter()

    if regulatory_context is None:
        regulatory_context = _default_regulatory_context()
    elif isinstance(regulatory_context, dict):
        regulatory_context = RegulatoryContext(**regulatory_context)

    if isinstance(code_attributes, dict):
        code_attributes = GeneratedCodeAttributes(**code_attributes)
    if isinstance(fim_positions, dict):
        fim_positions = FimPositions(**fim_positions)
    if isinstance(safety_review, dict):
        safety_review = SafetyCriticalReview(**safety_review)

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

    # Auto-infer line_count for generated_code when we have assistant text and
    # no explicit code_attributes were supplied.
    if (
        code_attributes is None
        and schema in ("generated_code/v1", "fim_completion/v1")
        and assistant_text is not None
    ):
        code_attributes = GeneratedCodeAttributes(
            language="unknown",
            line_count=assistant_text.count("\n"),
            has_security_pattern=False,
        )

    receipt = ReceiptV1(
        schema=schema,
        receipt_id=str(uuid.uuid4()),
        deployer_id=deployer_id,
        user_session_id=user_session_id,
        model=model_ref,
        content_refs=content_refs,
        regulatory_context=regulatory_context,
        code_attributes=code_attributes,
        fim_positions=fim_positions,
        safety_review=safety_review,
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


def emit_safety_critical_review_receipt(
    *,
    deployer_id: str,
    model_id: str,
    response_id: str,
    generated_code: str,
    reviewer_id: str,
    review_outcome: str,
    review_completed_at,
    review_policy_id: str,
    deployed: bool = False,
    deployment_target: str | None = None,
    language: str = "unknown",
    has_security_pattern: bool = False,
    static_analyser: str | None = None,
    signer: Signer | None = None,
    emitter: Emitter | None = None,
    user_session_id: str | None = None,
    regulatory_context: RegulatoryContext | dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Emit a safety_critical_code_review/v1 receipt.

    Use after a human reviewer has approved (or rejected) a generated code
    artefact and the result is about to be (or not be) deployed.

    The receipt does NOT contain the raw generated code — only its SHA-256 +
    byte length, plus deployer-asserted review metadata. Article 50(4)
    editorial-control evidence layer only; not a fitness-for-purpose
    certification.
    """
    signer = signer or Ed25519Signer()
    emitter = emitter or LogEmitter()

    if regulatory_context is None:
        regulatory_context = RegulatoryContext(
            article_50_paragraph="4",
            deployer_jurisdiction="EU",
            end_user_disclosure_made=True,
            notes="Article 50(4) editorial-control attestation for AI-generated code.",
        )
    elif isinstance(regulatory_context, dict):
        regulatory_context = RegulatoryContext(**regulatory_context)

    content_refs = [
        ContentRef(
            sha256_hex=hash_text(generated_code).hex(),
            byte_length=len(generated_code.encode("utf-8")),
            role="assistant",
        )
    ]

    code_attributes = GeneratedCodeAttributes(
        language=language.lower() if language else "unknown",
        line_count=generated_code.count("\n"),
        has_security_pattern=has_security_pattern,
        static_analyser=static_analyser,
    )

    safety_review = SafetyCriticalReview(
        reviewer_id=reviewer_id,
        review_outcome=review_outcome,  # type: ignore[arg-type]
        review_completed_at=review_completed_at,
        review_policy_id=review_policy_id,
        deployed=deployed,
        deployment_target=deployment_target,
    )

    receipt = ReceiptV1(
        schema="safety_critical_code_review/v1",
        receipt_id=str(uuid.uuid4()),
        deployer_id=deployer_id,
        user_session_id=user_session_id,
        model=ModelRef(model_id=model_id, response_id=response_id),
        content_refs=content_refs,
        regulatory_context=regulatory_context,
        code_attributes=code_attributes,
        safety_review=safety_review,
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
    Pull plain text out of a Codestral response, defensively.

    Codestral response shapes (mistralai>=1.0):
      chat:   response.choices[0].message.content       -> str | list
      FIM:    response.choices[0].message.content       -> str | list
              (FIM uses the same ChatCompletionResponse envelope)
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
    """Hash any function/tool calls present on a Codestral chat response."""
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
