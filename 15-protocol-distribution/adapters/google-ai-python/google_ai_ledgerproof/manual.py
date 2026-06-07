"""
Manual receipt emission. Use for full control over when and how a receipt fires —
for example inside a custom orchestration layer or non-standard Gemini call shape.
"""

from __future__ import annotations

import base64
import hashlib
import uuid
from typing import Any

from .canonical import canonical_encode, hash_text
from .emitter import Emitter, LogEmitter
from .schema import (
    ContentRef,
    FunctionCallRef,
    Modality,
    ModelRef,
    ReceiptV1,
    RegulatoryContext,
    SchemaName,
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
    function_calls: list[FunctionCallRef] | None = None,
    input_modalities: list[Modality] | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """
    Build, sign, and emit a receipt for a Gemini GenerateContentResponse.

    Returns the signed-receipt dict (also returned for inspection — never
    injected into `response`, per constraint C7).
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

    model_text = _extract_model_text(response)
    if model_text is not None:
        content_refs.append(
            ContentRef(
                sha256_hex=hash_text(model_text).hex(),
                byte_length=len(model_text.encode("utf-8")),
                role="model",
                modality="text",
            )
        )

    if not content_refs:
        content_refs.append(
            ContentRef(
                sha256_hex=hash_text("").hex(),
                byte_length=0,
                role="model",
                modality="text",
            )
        )

    model_ref = _build_model_ref(response)

    detected_calls = function_calls
    if detected_calls is None:
        detected_calls = extract_function_calls(response)

    # If function calls are present and the deployer hasn't overridden schema,
    # promote to the gemini_function_call/v1 receipt.
    effective_schema: SchemaName = schema
    if detected_calls and schema == "chatbot_session/v1":
        effective_schema = "gemini_function_call/v1"

    receipt = ReceiptV1(
        schema=effective_schema,
        receipt_id=str(uuid.uuid4()),
        deployer_id=deployer_id,
        session_id=session_id,
        model=model_ref,
        content_refs=content_refs,
        regulatory_context=regulatory_context,
        function_calls=detected_calls,
        input_modalities=input_modalities or ["text"],
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


# ---------------------------------------------------------------------------
# Response extraction helpers — defensive against partial / mocked responses.
# ---------------------------------------------------------------------------


def _extract_model_text(response: Any) -> str | None:
    """Pull plain text out of a Gemini GenerateContentResponse, defensively."""
    if response is None:
        return None

    # Direct .text accessor (preferred for non-streaming responses).
    text = getattr(response, "text", None)
    if isinstance(text, str) and text:
        return text

    # Fall back to candidates[].content.parts[].text
    candidates = getattr(response, "candidates", None) or []
    chunks: list[str] = []
    for cand in candidates:
        content = getattr(cand, "content", None)
        if content is None:
            continue
        parts = getattr(content, "parts", None) or []
        for part in parts:
            part_text = getattr(part, "text", None)
            if isinstance(part_text, str):
                chunks.append(part_text)
    return "".join(chunks) if chunks else None


def _build_model_ref(response: Any) -> ModelRef:
    """Build a ModelRef from a Gemini response (or fall back gracefully)."""
    if response is None:
        return ModelRef(model_id="unknown", response_id="unknown")

    response_id = (
        getattr(response, "response_id", None)
        or getattr(response, "id", None)
        or "unknown"
    )
    # Model id can hang off the response or its `_model` private attr depending
    # on SDK version. Try a few locations.
    model_id = (
        getattr(response, "model_version", None)
        or getattr(response, "model", None)
        or "unknown"
    )

    finish_reason = None
    candidates = getattr(response, "candidates", None) or []
    if candidates:
        fr = getattr(candidates[0], "finish_reason", None)
        if fr is not None:
            finish_reason = str(fr)

    usage = getattr(response, "usage_metadata", None)
    prompt_tokens = getattr(usage, "prompt_token_count", None) if usage else None
    candidate_tokens = (
        getattr(usage, "candidates_token_count", None) if usage else None
    )
    total_tokens = getattr(usage, "total_token_count", None) if usage else None

    return ModelRef(
        model_id=str(model_id),
        response_id=str(response_id),
        finish_reason=finish_reason,
        prompt_token_count=prompt_tokens,
        candidates_token_count=candidate_tokens,
        total_token_count=total_tokens,
    )


def extract_function_calls(response: Any) -> list[FunctionCallRef]:
    """
    Inspect a Gemini response for function-call parts and hash their arguments.

    Gemini surfaces tool calls as Parts with a `.function_call` attribute that
    has `.name` and `.args` (a Mapping-like, often a proto Struct).
    """
    refs: list[FunctionCallRef] = []
    candidates = getattr(response, "candidates", None) or []
    for cand in candidates:
        content = getattr(cand, "content", None)
        if content is None:
            continue
        parts = getattr(content, "parts", None) or []
        for part in parts:
            fc = getattr(part, "function_call", None)
            if fc is None:
                continue
            name = getattr(fc, "name", None) or "unknown"
            args = getattr(fc, "args", None)
            args_bytes = _safe_canonical_bytes(args)
            refs.append(
                FunctionCallRef(
                    function_name=str(name)[:128],
                    args_sha256_hex=hashlib.sha256(args_bytes).hexdigest(),
                )
            )
    return refs


def _safe_canonical_bytes(value: Any) -> bytes:
    """Best-effort canonicalization for unknown structures (proto Structs etc.)."""
    if value is None:
        return b""
    if isinstance(value, (bytes, bytearray)):
        return bytes(value)
    if isinstance(value, str):
        return value.encode("utf-8")
    # Try dict-coercion first (proto Struct supports dict(value) or .items()).
    try:
        as_dict = dict(value)
        return canonical_encode(as_dict)
    except Exception:
        pass
    try:
        return canonical_encode({"_repr": repr(value)})
    except Exception:
        return repr(value).encode("utf-8")
