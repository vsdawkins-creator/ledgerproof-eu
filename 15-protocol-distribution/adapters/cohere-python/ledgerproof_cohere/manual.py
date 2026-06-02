"""
Manual receipt emission for Cohere ChatResponse-shaped objects.

Use for full control over when and how a receipt fires, for example inside a
custom orchestration layer or non-standard Cohere call shape (Embed-only flows,
Rerank-only flows, Classify pipelines).
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
    DisclosureRef,
    ModelRef,
    ReceiptV1,
    RegulatoryContext,
    RetrievedDocumentRef,
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
    retrieved_documents: list[RetrievedDocumentRef] | None = None,
    disclosure: DisclosureRef | None = None,
) -> dict[str, Any]:
    """
    Build, sign, and emit a receipt for a Cohere ChatResponse.

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

    # Extract assistant text from the Cohere response.
    assistant_text = extract_assistant_text(response)
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

    model_ref = build_model_ref(response)

    receipt_kwargs = dict(
        schema=schema,
        receipt_id=str(uuid.uuid4()),
        deployer_id=deployer_id,
        model=model_ref,
        content_refs=content_refs,
        regulatory_context=regulatory_context,
        tool_uses=tool_uses or [],
        retrieved_documents=retrieved_documents or [],
        streaming=streaming,
        adapter_version=__version__,
    )
    if disclosure is not None:
        receipt_kwargs["disclosure"] = disclosure

    receipt = ReceiptV1(**receipt_kwargs)

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


def extract_assistant_text(response: Any) -> str | None:
    """
    Pull plain text out of a Cohere ChatResponse, defensively.

    Cohere V2 ChatResponse shape:
        response.message.content : list[ {type:"text", text: "..."} ]
        response.message.content[0].text

    We also tolerate dict-shaped responses, .text attribute (legacy V1), and
    SimpleNamespace test fixtures.
    """
    if response is None:
        return None

    # V2 shape: response.message.content[*].text
    message = getattr(response, "message", None)
    if message is not None:
        content = getattr(message, "content", None)
        if content is None and isinstance(message, dict):
            content = message.get("content")
        if content is not None:
            chunks = _extract_text_chunks(content)
            if chunks:
                return "".join(chunks)
        # Some V2 streams expose message.text directly.
        text_attr = getattr(message, "text", None)
        if isinstance(text_attr, str):
            return text_attr

    # Legacy V1 fallback: response.text
    text_attr = getattr(response, "text", None)
    if isinstance(text_attr, str):
        return text_attr

    # Dict-shaped response.
    if isinstance(response, dict):
        if "message" in response:
            chunks = _extract_text_chunks(response["message"].get("content"))
            if chunks:
                return "".join(chunks)
        if isinstance(response.get("text"), str):
            return response["text"]

    return None


def _extract_text_chunks(content: Any) -> list[str]:
    if content is None:
        return []
    if isinstance(content, str):
        return [content]
    chunks: list[str] = []
    if isinstance(content, list):
        for block in content:
            text = None
            if isinstance(block, dict):
                if block.get("type") in (None, "text"):
                    text = block.get("text")
            else:
                text = getattr(block, "text", None)
            if isinstance(text, str):
                chunks.append(text)
    return chunks


def build_model_ref(response: Any) -> ModelRef:
    response_id = getattr(response, "id", None) or _dict_get(response, "id") or "unknown"
    model_id = (
        getattr(response, "model", None)
        or _dict_get(response, "model")
        or "unknown"
    )
    finish_reason = getattr(response, "finish_reason", None) or _dict_get(response, "finish_reason")
    usage = getattr(response, "usage", None) or _dict_get(response, "usage")

    input_tokens = None
    output_tokens = None
    if usage is not None:
        # Cohere V2 usage: usage.tokens.input_tokens, usage.tokens.output_tokens
        tokens = getattr(usage, "tokens", None) or _dict_get(usage, "tokens")
        if tokens is not None:
            input_tokens = getattr(tokens, "input_tokens", None) or _dict_get(tokens, "input_tokens")
            output_tokens = getattr(tokens, "output_tokens", None) or _dict_get(tokens, "output_tokens")
        # Fallback: usage.input_tokens, usage.output_tokens
        if input_tokens is None:
            input_tokens = getattr(usage, "input_tokens", None) or _dict_get(usage, "input_tokens")
        if output_tokens is None:
            output_tokens = getattr(usage, "output_tokens", None) or _dict_get(usage, "output_tokens")

    return ModelRef(
        model_id=str(model_id),
        response_id=str(response_id),
        finish_reason=str(finish_reason) if finish_reason else None,
        input_tokens=int(input_tokens) if input_tokens is not None else None,
        output_tokens=int(output_tokens) if output_tokens is not None else None,
    )


def _dict_get(obj: Any, key: str) -> Any:
    if isinstance(obj, dict):
        return obj.get(key)
    return None


def extract_tool_uses(response: Any) -> list[ToolUseRef]:
    """
    Inspect a Cohere V2 ChatResponse for tool_calls and hash them.

    Cohere V2 places tool calls on `response.message.tool_calls` as a list with
    fields `.id`, `.function.name`, `.function.arguments` (JSON string).
    """
    refs: list[ToolUseRef] = []
    message = getattr(response, "message", None)
    if message is None and isinstance(response, dict):
        message = response.get("message")
    if message is None:
        return refs
    tool_calls = getattr(message, "tool_calls", None)
    if tool_calls is None and isinstance(message, dict):
        tool_calls = message.get("tool_calls")
    if not tool_calls:
        return refs

    for call in tool_calls:
        tool_call_id = getattr(call, "id", None) or _dict_get(call, "id") or "unknown"
        function = getattr(call, "function", None) or _dict_get(call, "function")
        tool_name = "unknown"
        tool_args: str | dict | None = None
        if function is not None:
            tool_name = (
                getattr(function, "name", None)
                or _dict_get(function, "name")
                or "unknown"
            )
            tool_args = (
                getattr(function, "arguments", None)
                or _dict_get(function, "arguments")
            )
        if tool_args is None:
            args_bytes = b""
        elif isinstance(tool_args, str):
            args_bytes = tool_args.encode("utf-8")
        else:
            try:
                args_bytes = canonical_encode(tool_args) if isinstance(tool_args, dict) else repr(tool_args).encode("utf-8")
            except Exception:
                args_bytes = repr(tool_args).encode("utf-8")

        refs.append(
            ToolUseRef(
                tool_name=str(tool_name)[:128],
                tool_call_id=str(tool_call_id)[:128],
                input_sha256_hex=hashlib.sha256(args_bytes).hexdigest(),
            )
        )
    return refs


def build_retrieved_document_refs(
    documents: list[dict[str, Any]],
    rerank_results: list[Any] | None = None,
) -> list[RetrievedDocumentRef]:
    """
    Build RetrievedDocumentRef list from a list of documents and optional Rerank
    results. Each document dict should have at least:
        - "id" or "document_id": stable identifier
        - "text" or "snippet": the retrieved content
        - optional "source_uri"

    If rerank_results is provided (output of `co.rerank(...)`), each result is
    expected to expose `.index` (into the original `documents` list) and
    `.relevance_score`.
    """
    if rerank_results:
        rerank_lookup: dict[int, tuple[float, int]] = {}
        for rank_pos, r in enumerate(rerank_results):
            idx = getattr(r, "index", None)
            if idx is None and isinstance(r, dict):
                idx = r.get("index")
            score = getattr(r, "relevance_score", None)
            if score is None and isinstance(r, dict):
                score = r.get("relevance_score")
            if idx is not None:
                rerank_lookup[int(idx)] = (float(score) if score is not None else 0.0, rank_pos)
    else:
        rerank_lookup = {}

    refs: list[RetrievedDocumentRef] = []
    for i, doc in enumerate(documents):
        doc_id = str(doc.get("id") or doc.get("document_id") or f"doc-{i}")[:256]
        text = doc.get("text") or doc.get("snippet") or ""
        encoded = text.encode("utf-8") if isinstance(text, str) else bytes(text)
        score, rerank_idx = rerank_lookup.get(i, (None, None))
        refs.append(
            RetrievedDocumentRef(
                document_id=doc_id,
                sha256_hex=hashlib.sha256(encoded).hexdigest(),
                byte_length=len(encoded),
                rerank_relevance_score=score,
                rerank_index=rerank_idx,
                source_uri=str(doc["source_uri"])[:512] if doc.get("source_uri") else None,
            )
        )
    return refs


def build_disclosure_ref(
    disclosure_text: str,
    language_tag: str,
    *,
    channel: str | None = None,
) -> DisclosureRef:
    """
    Build a DisclosureRef capturing the language and hash of the disclosure
    string actually shown to the end user (Article 50(5)).
    """
    encoded = disclosure_text.encode("utf-8")
    return DisclosureRef(
        language_tag=language_tag,
        disclosure_sha256_hex=hashlib.sha256(encoded).hexdigest(),
        disclosure_byte_length=len(encoded),
        disclosure_channel=channel,
    )
