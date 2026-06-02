"""
Synchronous client wrapper around `cohere.ClientV2`.

Intercepts `chat()` and `chat_stream()` to emit a receipt on the side channel
(constraint C7) after the response is materialised. The wrapped response object
is returned unchanged.

Also exposes a `rerank()` passthrough that lets callers tag a follow-up `chat()`
as a RAG response by binding the retrieved documents into a `rag_response/v1`
receipt — see `LedgerProofCohere.chat_with_retrieved_documents()`.
"""

from __future__ import annotations

import base64
import logging
import uuid
from typing import Any, Iterator

from .canonical import IncrementalTextHasher, canonical_encode, hash_text
from .emitter import Emitter, LogEmitter
from .manual import (
    build_disclosure_ref,
    build_model_ref,
    build_retrieved_document_refs,
    extract_assistant_text,
    extract_tool_uses,
)
from .schema import (
    ContentRef,
    DisclosureRef,
    ReceiptV1,
    RegulatoryContext,
    RetrievedDocumentRef,
    SchemaName,
)
from .signer import Ed25519Signer, Signer
from .version import __version__

logger = logging.getLogger(__name__)


def _extract_user_message_text(messages: list[dict[str, Any]] | None) -> str:
    """Best-effort concatenation of user-role text from a Cohere V2 messages list."""
    if not messages:
        return ""
    parts: list[str] = []
    for msg in messages:
        if not isinstance(msg, dict):
            # Pydantic model from cohere — fall back to attribute access.
            role = getattr(msg, "role", None)
            content = getattr(msg, "content", None)
        else:
            role = msg.get("role")
            content = msg.get("content")
        if role != "user":
            continue
        if isinstance(content, str):
            parts.append(content)
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") in (None, "text"):
                    parts.append(str(block.get("text", "")))
                else:
                    text = getattr(block, "text", None)
                    if isinstance(text, str):
                        parts.append(text)
    return "\n".join(parts)


def _default_reg_ctx() -> RegulatoryContext:
    return RegulatoryContext(
        article_50_paragraph="1",
        deployer_jurisdiction="EU",
        end_user_disclosure_made=True,
    )


class LedgerProofCohere:
    """
    Drop-in wrapper for `cohere.ClientV2`.

    Usage:
        import cohere
        from ledgerproof_cohere import LedgerProofCohere

        client = LedgerProofCohere(deployer_id="acme-eu", api_key="...")
        response = client.chat(
            model="command-a-03-2025",
            messages=[{"role": "user", "content": "Hello"}],
        )

    All other attributes/methods of the underlying ClientV2 are forwarded
    (`embed`, `rerank`, `classify`, etc.).
    """

    def __init__(
        self,
        deployer_id: str,
        *,
        client: Any | None = None,
        signer: Signer | None = None,
        emitter: Emitter | None = None,
        regulatory_context: RegulatoryContext | dict[str, Any] | None = None,
        schema: SchemaName = "chatbot_session/v1",
        api_key: str | None = None,
        **cohere_kwargs: Any,
    ):
        self.deployer_id = deployer_id
        if client is None:
            import cohere
            client = cohere.ClientV2(api_key=api_key, **cohere_kwargs)
        self._inner = client
        self._signer: Signer = signer or Ed25519Signer()
        self._emitter: Emitter = emitter or LogEmitter()
        self._schema: SchemaName = schema
        if isinstance(regulatory_context, dict):
            regulatory_context = RegulatoryContext(**regulatory_context)
        self._reg_ctx: RegulatoryContext = regulatory_context or _default_reg_ctx()

    # ------------------------------------------------------------------
    # Pass-through to the underlying ClientV2 for any non-intercepted attribute.
    # ------------------------------------------------------------------
    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    # ------------------------------------------------------------------
    # chat() — non-streaming
    # ------------------------------------------------------------------
    def chat(self, *args: Any, **kwargs: Any) -> Any:
        response = self._inner.chat(*args, **kwargs)
        try:
            self._emit_for_response(
                response=response,
                user_message_text=_extract_user_message_text(kwargs.get("messages")),
                streaming=False,
            )
        except Exception as exc:  # noqa: BLE001
            # C7: never break the calling code path.
            logger.warning("LedgerProof receipt emission failed: %s", exc)
        return response

    # ------------------------------------------------------------------
    # chat_stream() — streaming
    # ------------------------------------------------------------------
    def chat_stream(self, *args: Any, **kwargs: Any) -> Iterator[Any]:
        """
        Wrap `cohere.ClientV2.chat_stream`. Yields stream events unchanged
        (constraint C7). After the stream completes, a receipt is emitted on
        the side channel using the incremental hash of `content-delta` events.

        Cohere V2 stream events carry text deltas under
            event.delta.message.content.text
        for type == "content-delta", and the final ChatResponse on the
        "message-end" event under event.response.
        """
        hasher = IncrementalTextHasher()
        user_text = _extract_user_message_text(kwargs.get("messages"))
        final_response: Any = None
        finish_reason: str | None = None
        response_id: str | None = None
        model_id: str | None = kwargs.get("model")
        input_tokens: int | None = None
        output_tokens: int | None = None
        tool_calls_accum: list[Any] = []

        try:
            for event in self._inner.chat_stream(*args, **kwargs):
                # Tap text deltas for incremental hashing.
                delta_text = _extract_delta_text(event)
                if delta_text:
                    hasher.update(delta_text)

                # Capture useful metadata as it streams past.
                etype = getattr(event, "type", None) or _safe_dict_get(event, "type")
                if etype == "message-start":
                    response_id = response_id or _safe_dict_get(event, "id") or getattr(event, "id", None)
                if etype == "message-end":
                    # Cohere V2 emits the final ChatResponse here.
                    final_response = getattr(event, "response", None) or _safe_dict_get(event, "response") or event
                    finish_reason = (
                        getattr(event, "finish_reason", None)
                        or _safe_dict_get(event, "finish_reason")
                        or _get_finish_reason(final_response)
                    )
                    usage = _get_usage(final_response) or _safe_dict_get(event, "usage")
                    if usage is not None:
                        input_tokens, output_tokens = _extract_tokens(usage)

                yield event
        finally:
            try:
                self._emit_for_stream(
                    final_response=final_response,
                    user_message_text=user_text,
                    text_hasher=hasher,
                    fallback_model_id=model_id,
                    fallback_response_id=response_id,
                    fallback_finish_reason=finish_reason,
                    fallback_input_tokens=input_tokens,
                    fallback_output_tokens=output_tokens,
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("LedgerProof streaming receipt failed: %s", exc)

    # ------------------------------------------------------------------
    # RAG convenience — chat with retrieved-document attestation
    # ------------------------------------------------------------------
    def chat_with_retrieved_documents(
        self,
        *,
        documents: list[dict[str, Any]],
        rerank_results: list[Any] | None = None,
        **chat_kwargs: Any,
    ) -> Any:
        """
        Call `chat()` and emit a `rag_response/v1` receipt that binds the SHA-256
        of every retrieved document (and Rerank score, if provided) to the
        response signature.

        The Cohere SDK lets you pass retrieved documents to `chat()` via the
        `documents=` kwarg; this helper forwards them while also recording the
        attestation. If `documents` is in dict form `{"id":..., "text":...}`,
        each entry is hashed and bound.
        """
        # Cohere V2 accepts `documents=` directly on chat for grounded answers.
        if "documents" not in chat_kwargs:
            chat_kwargs["documents"] = documents

        response = self._inner.chat(**chat_kwargs)
        try:
            retrieved_refs = build_retrieved_document_refs(documents, rerank_results=rerank_results)
            self._emit_for_response(
                response=response,
                user_message_text=_extract_user_message_text(chat_kwargs.get("messages")),
                streaming=False,
                retrieved_documents=retrieved_refs,
                schema_override="rag_response/v1",
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("LedgerProof RAG receipt emission failed: %s", exc)
        return response

    # ------------------------------------------------------------------
    # Multilingual disclosure — bind the language of the disclosure shown
    # ------------------------------------------------------------------
    def chat_with_disclosure(
        self,
        *,
        disclosure_text: str,
        disclosure_language: str,
        disclosure_channel: str | None = None,
        **chat_kwargs: Any,
    ) -> Any:
        """
        Call `chat()` and emit a `multilingual_disclosure/v1` receipt binding
        the exact disclosure text (e.g. "Sie chatten mit einer KI") and its
        language tag to the response signature.

        The disclosure text is hashed; raw text is not stored.
        """
        response = self._inner.chat(**chat_kwargs)
        try:
            disclosure = build_disclosure_ref(
                disclosure_text=disclosure_text,
                language_tag=disclosure_language,
                channel=disclosure_channel,
            )
            self._emit_for_response(
                response=response,
                user_message_text=_extract_user_message_text(chat_kwargs.get("messages")),
                streaming=False,
                disclosure=disclosure,
                schema_override="multilingual_disclosure/v1",
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("LedgerProof multilingual disclosure receipt emission failed: %s", exc)
        return response

    # ------------------------------------------------------------------
    # Internal: receipt construction
    # ------------------------------------------------------------------
    def _emit_for_response(
        self,
        response: Any,
        user_message_text: str,
        streaming: bool,
        retrieved_documents: list[RetrievedDocumentRef] | None = None,
        disclosure: DisclosureRef | None = None,
        schema_override: SchemaName | None = None,
    ) -> None:
        content_refs: list[ContentRef] = []
        if user_message_text:
            content_refs.append(
                ContentRef(
                    sha256_hex=hash_text(user_message_text).hex(),
                    byte_length=len(user_message_text.encode("utf-8")),
                    role="user",
                )
            )
        assistant_text = extract_assistant_text(response) or ""
        content_refs.append(
            ContentRef(
                sha256_hex=hash_text(assistant_text).hex(),
                byte_length=len(assistant_text.encode("utf-8")),
                role="assistant",
            )
        )
        tool_uses = extract_tool_uses(response)
        # Schema selection priority:
        # 1. explicit override
        # 2. retrieved_documents present -> rag_response/v1
        # 3. tool_uses present -> generated_content/v1 (Cohere has no agent
        #    schema; tool use here is captured under generated_content)
        # 4. configured default
        if schema_override is not None:
            schema = schema_override
        elif retrieved_documents:
            schema = "rag_response/v1"
        else:
            schema = self._schema

        self._build_and_emit(
            response=response,
            content_refs=content_refs,
            tool_uses=tool_uses,
            streaming=streaming,
            schema_override=schema,
            retrieved_documents=retrieved_documents or [],
            disclosure=disclosure,
        )

    def _emit_for_stream(
        self,
        final_response: Any,
        user_message_text: str,
        text_hasher: IncrementalTextHasher,
        fallback_model_id: str | None,
        fallback_response_id: str | None,
        fallback_finish_reason: str | None,
        fallback_input_tokens: int | None,
        fallback_output_tokens: int | None,
    ) -> None:
        content_refs: list[ContentRef] = []
        if user_message_text:
            content_refs.append(
                ContentRef(
                    sha256_hex=hash_text(user_message_text).hex(),
                    byte_length=len(user_message_text.encode("utf-8")),
                    role="user",
                )
            )
        content_refs.append(
            ContentRef(
                sha256_hex=text_hasher.digest().hex(),
                byte_length=text_hasher.byte_count,
                role="assistant",
            )
        )
        tool_uses = extract_tool_uses(final_response) if final_response is not None else []
        schema = "generated_content/v1" if tool_uses and self._schema == "chatbot_session/v1" else self._schema

        if final_response is not None:
            model_ref = build_model_ref(final_response)
        else:
            from .schema import ModelRef
            model_ref = ModelRef(
                model_id=fallback_model_id or "unknown",
                response_id=fallback_response_id or "unknown",
                finish_reason=fallback_finish_reason,
                input_tokens=fallback_input_tokens,
                output_tokens=fallback_output_tokens,
            )

        self._build_and_emit_with_model_ref(
            model_ref=model_ref,
            content_refs=content_refs,
            tool_uses=tool_uses,
            streaming=True,
            schema_override=schema,
            retrieved_documents=[],
            disclosure=None,
        )

    def _build_and_emit(
        self,
        response: Any,
        content_refs: list[ContentRef],
        tool_uses: list,
        streaming: bool,
        schema_override: SchemaName,
        retrieved_documents: list[RetrievedDocumentRef],
        disclosure: DisclosureRef | None,
    ) -> None:
        if response is not None:
            model_ref = build_model_ref(response)
        else:
            from .schema import ModelRef
            model_ref = ModelRef(model_id="unknown", response_id="unknown")
        self._build_and_emit_with_model_ref(
            model_ref=model_ref,
            content_refs=content_refs,
            tool_uses=tool_uses,
            streaming=streaming,
            schema_override=schema_override,
            retrieved_documents=retrieved_documents,
            disclosure=disclosure,
        )

    def _build_and_emit_with_model_ref(
        self,
        model_ref,
        content_refs: list[ContentRef],
        tool_uses: list,
        streaming: bool,
        schema_override: SchemaName,
        retrieved_documents: list[RetrievedDocumentRef],
        disclosure: DisclosureRef | None,
    ) -> None:
        receipt_kwargs = dict(
            schema=schema_override,
            receipt_id=str(uuid.uuid4()),
            deployer_id=self.deployer_id,
            model=model_ref,
            content_refs=content_refs,
            regulatory_context=self._reg_ctx,
            tool_uses=tool_uses,
            retrieved_documents=retrieved_documents,
            streaming=streaming,
            adapter_version=__version__,
        )
        if disclosure is not None:
            receipt_kwargs["disclosure"] = disclosure

        receipt = ReceiptV1(**receipt_kwargs)
        payload = receipt.to_payload()
        canonical_bytes = canonical_encode(payload)
        signature = self._signer.sign(canonical_bytes)
        signed = {
            "receipt": payload,
            "signature_alg": "ed25519",
            "signature_b64": base64.b64encode(signature).decode("ascii"),
            "signer_key_id": self._signer.key_id,
            "canonical_encoding": "cbor-rfc8949-deterministic",
        }
        self._emitter.emit(signed)


# ---------------------------------------------------------------------------
# Stream-event helpers (Cohere V2 chat_stream event shape)
# ---------------------------------------------------------------------------


def _safe_dict_get(obj: Any, key: str) -> Any:
    if isinstance(obj, dict):
        return obj.get(key)
    return None


def _extract_delta_text(event: Any) -> str | None:
    """
    Pull text out of a Cohere V2 streaming event. The event shape for
    `content-delta` is roughly:
        event.type == "content-delta"
        event.delta.message.content.text == "..."
    We probe defensively across attribute and dict access.
    """
    etype = getattr(event, "type", None) or _safe_dict_get(event, "type")
    if etype is not None and etype != "content-delta":
        return None

    delta = getattr(event, "delta", None) or _safe_dict_get(event, "delta")
    if delta is None:
        return None
    message = getattr(delta, "message", None) or _safe_dict_get(delta, "message")
    if message is None:
        return None
    content = getattr(message, "content", None) or _safe_dict_get(message, "content")
    if content is None:
        return None
    text = getattr(content, "text", None) or _safe_dict_get(content, "text")
    if isinstance(text, str):
        return text
    # Some shapes put content as a list of blocks.
    if isinstance(content, list):
        for block in content:
            block_text = getattr(block, "text", None) or _safe_dict_get(block, "text")
            if isinstance(block_text, str):
                return block_text
    return None


def _get_finish_reason(response: Any) -> str | None:
    if response is None:
        return None
    fr = getattr(response, "finish_reason", None) or _safe_dict_get(response, "finish_reason")
    return str(fr) if fr else None


def _get_usage(response: Any) -> Any:
    if response is None:
        return None
    return getattr(response, "usage", None) or _safe_dict_get(response, "usage")


def _extract_tokens(usage: Any) -> tuple[int | None, int | None]:
    tokens = getattr(usage, "tokens", None) or _safe_dict_get(usage, "tokens")
    if tokens is not None:
        i = getattr(tokens, "input_tokens", None) or _safe_dict_get(tokens, "input_tokens")
        o = getattr(tokens, "output_tokens", None) or _safe_dict_get(tokens, "output_tokens")
        return (int(i) if i is not None else None, int(o) if o is not None else None)
    i = getattr(usage, "input_tokens", None) or _safe_dict_get(usage, "input_tokens")
    o = getattr(usage, "output_tokens", None) or _safe_dict_get(usage, "output_tokens")
    return (int(i) if i is not None else None, int(o) if o is not None else None)
