"""
Async client wrapper around `cohere.AsyncClientV2`. Mirror of client_wrapper.py.
"""

from __future__ import annotations

import logging
from typing import Any, AsyncIterator

from .canonical import IncrementalTextHasher
from .client_wrapper import (
    LedgerProofCohere,
    _default_reg_ctx,
    _extract_delta_text,
    _extract_tokens,
    _extract_user_message_text,
    _get_finish_reason,
    _get_usage,
    _safe_dict_get,
)
from .emitter import Emitter, LogEmitter
from .manual import build_disclosure_ref, build_retrieved_document_refs
from .schema import RegulatoryContext, SchemaName
from .signer import Ed25519Signer, Signer

logger = logging.getLogger(__name__)


class LedgerProofAsyncCohere(LedgerProofCohere):
    """
    Async drop-in wrapper for `cohere.AsyncClientV2`.

    Usage:
        client = LedgerProofAsyncCohere(deployer_id="acme-eu", api_key="...")
        response = await client.chat(model="command-a-03-2025", messages=[...])
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
        # Don't call super().__init__ — it would build a sync ClientV2.
        self.deployer_id = deployer_id
        if client is None:
            import cohere
            client = cohere.AsyncClientV2(api_key=api_key, **cohere_kwargs)
        self._inner = client
        self._signer: Signer = signer or Ed25519Signer()
        self._emitter: Emitter = emitter or LogEmitter()
        self._schema: SchemaName = schema
        if isinstance(regulatory_context, dict):
            regulatory_context = RegulatoryContext(**regulatory_context)
        self._reg_ctx: RegulatoryContext = regulatory_context or _default_reg_ctx()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    # ------------------------------------------------------------------
    # chat() — non-streaming, async
    # ------------------------------------------------------------------
    async def chat(self, *args: Any, **kwargs: Any) -> Any:  # type: ignore[override]
        response = await self._inner.chat(*args, **kwargs)
        try:
            self._emit_for_response(
                response=response,
                user_message_text=_extract_user_message_text(kwargs.get("messages")),
                streaming=False,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("LedgerProof async receipt emission failed: %s", exc)
        return response

    # ------------------------------------------------------------------
    # chat_stream() — streaming, async generator
    # ------------------------------------------------------------------
    async def chat_stream(self, *args: Any, **kwargs: Any) -> AsyncIterator[Any]:  # type: ignore[override]
        hasher = IncrementalTextHasher()
        user_text = _extract_user_message_text(kwargs.get("messages"))
        final_response: Any = None
        finish_reason: str | None = None
        response_id: str | None = None
        model_id: str | None = kwargs.get("model")
        input_tokens: int | None = None
        output_tokens: int | None = None

        try:
            async for event in self._inner.chat_stream(*args, **kwargs):
                delta_text = _extract_delta_text(event)
                if delta_text:
                    hasher.update(delta_text)

                etype = getattr(event, "type", None) or _safe_dict_get(event, "type")
                if etype == "message-start":
                    response_id = response_id or _safe_dict_get(event, "id") or getattr(event, "id", None)
                if etype == "message-end":
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
                logger.warning("LedgerProof async streaming receipt failed: %s", exc)

    # ------------------------------------------------------------------
    # RAG + multilingual variants (async)
    # ------------------------------------------------------------------
    async def chat_with_retrieved_documents(  # type: ignore[override]
        self,
        *,
        documents: list[dict[str, Any]],
        rerank_results: list[Any] | None = None,
        **chat_kwargs: Any,
    ) -> Any:
        if "documents" not in chat_kwargs:
            chat_kwargs["documents"] = documents
        response = await self._inner.chat(**chat_kwargs)
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
            logger.warning("LedgerProof async RAG receipt emission failed: %s", exc)
        return response

    async def chat_with_disclosure(  # type: ignore[override]
        self,
        *,
        disclosure_text: str,
        disclosure_language: str,
        disclosure_channel: str | None = None,
        **chat_kwargs: Any,
    ) -> Any:
        response = await self._inner.chat(**chat_kwargs)
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
            logger.warning("LedgerProof async multilingual disclosure receipt failed: %s", exc)
        return response
