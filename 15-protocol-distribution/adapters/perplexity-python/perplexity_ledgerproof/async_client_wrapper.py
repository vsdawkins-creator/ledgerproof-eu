"""Async client wrapper — mirrors `client_wrapper.py` for `openai.AsyncOpenAI`
pointed at Perplexity AI's OpenAI-compatible API.
"""

from __future__ import annotations

import hashlib
import os
import uuid
from typing import Any, AsyncIterator

from openai import AsyncOpenAI

from .canonical import citation_list_hash_hex
from .client_wrapper import (
    PERPLEXITY_DEFAULT_BASE_URL,
    _CITATION_SCHEMAS,
    _SignedReceiptBuilder,
    _extract_chunk_citations,
    _extract_chunk_text,
    _hash_messages,
    _hash_non_streaming_response,
)
from .emitter import Emitter, LogEmitter
from .manual import extract_citations
from .signer import Ed25519Signer, Signer


class _AsyncStreamingProxy:
    """Async wrapper that emits a receipt once the stream is drained."""

    def __init__(
        self,
        stream: AsyncIterator[Any],
        *,
        builder: _SignedReceiptBuilder,
        prompt_sha256: str,
        fallback_interaction_id: str,
    ) -> None:
        self._stream = stream
        self._builder = builder
        self._prompt_sha256 = prompt_sha256
        self._fallback_interaction_id = fallback_interaction_id
        self._hasher = hashlib.sha256()
        self._model_id = "unknown"
        self._interaction_id: str | None = None
        self._citations: set[str] = set()
        self._emitted = False

    def __aiter__(self) -> "_AsyncStreamingProxy":
        return self

    async def __anext__(self) -> Any:
        try:
            chunk = await self._stream.__anext__()
        except StopAsyncIteration:
            self._flush()
            raise
        self._absorb(chunk)
        return chunk

    async def __aenter__(self) -> "_AsyncStreamingProxy":
        return self

    async def __aexit__(self, *exc: Any) -> None:
        self._flush()
        close = getattr(self._stream, "aclose", None)
        if callable(close):
            await close()

    def _absorb(self, chunk: Any) -> None:
        if self._interaction_id is None:
            self._interaction_id = getattr(chunk, "id", None)
        model = getattr(chunk, "model", None)
        if model:
            self._model_id = model
        text = _extract_chunk_text(chunk)
        if text:
            self._hasher.update(text.encode("utf-8"))
        for url in _extract_chunk_citations(chunk):
            self._citations.add(url)

    def _flush(self) -> None:
        if self._emitted:
            return
        self._emitted = True
        schema = self._builder.regulatory_context.get("schema", "chatbot_session/v1")
        extra_fields: dict[str, Any] = {}
        if schema in _CITATION_SCHEMAS:
            cites = sorted(self._citations)
            extra_fields["citations_sha256"] = citation_list_hash_hex(cites)
            extra_fields["citations_count"] = len(cites)
        self._builder.emit(
            model_id=self._model_id,
            interaction_id=self._interaction_id or self._fallback_interaction_id,
            prompt_sha256=self._prompt_sha256,
            response_sha256=self._hasher.hexdigest(),
            extra={"streaming": True, "provider": "perplexity"},
            extra_fields=extra_fields or None,
        )


class _AsyncChatCompletionsProxy:
    def __init__(self, inner: Any, builder: _SignedReceiptBuilder) -> None:
        self._inner = inner
        self._builder = builder

    async def create(self, *args: Any, **kwargs: Any) -> Any:
        messages = kwargs.get("messages")
        prompt_sha256 = _hash_messages(messages)
        streaming = bool(kwargs.get("stream"))
        result = await self._inner.create(*args, **kwargs)

        if streaming:
            return _AsyncStreamingProxy(
                result,
                builder=self._builder,
                prompt_sha256=prompt_sha256,
                fallback_interaction_id=str(uuid.uuid4()),
            )

        schema = self._builder.regulatory_context.get("schema", "chatbot_session/v1")
        extra_fields: dict[str, Any] = {}
        extra: dict[str, Any] = {"provider": "perplexity"}

        if schema in _CITATION_SCHEMAS:
            preset_hash = self._builder.regulatory_context.get("citations_sha256")
            preset_count = self._builder.regulatory_context.get("citations_count")
            if preset_hash:
                extra_fields["citations_sha256"] = preset_hash
                if preset_count is not None:
                    extra_fields["citations_count"] = int(preset_count)
            else:
                cites = extract_citations(result)
                extra_fields["citations_sha256"] = citation_list_hash_hex(cites)
                extra_fields["citations_count"] = len(cites)

        if schema == "public_interest_text/v1":
            for k in ("disclosure_label_shown", "editorial_review", "subject_category"):
                if k in self._builder.regulatory_context:
                    extra_fields[k] = self._builder.regulatory_context[k]

        self._builder.emit(
            model_id=getattr(result, "model", "unknown"),
            interaction_id=getattr(result, "id", None) or str(uuid.uuid4()),
            prompt_sha256=prompt_sha256,
            response_sha256=_hash_non_streaming_response(result),
            extra=extra,
            extra_fields=extra_fields or None,
        )
        return result

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)


class _AsyncChatProxy:
    def __init__(self, inner: Any, builder: _SignedReceiptBuilder) -> None:
        self._inner = inner
        self._builder = builder
        self.completions = _AsyncChatCompletionsProxy(inner.completions, builder)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)


class LedgerProofAsyncPerplexity:
    """Async sibling of `LedgerProofPerplexity`."""

    def __init__(
        self,
        deployer_id: str,
        *,
        regulatory_context: dict[str, Any] | None = None,
        signer: Signer | None = None,
        emitter: Emitter | None = None,
        openai_client: AsyncOpenAI | None = None,
        **openai_kwargs: Any,
    ) -> None:
        if openai_client is None:
            openai_kwargs.setdefault("base_url", PERPLEXITY_DEFAULT_BASE_URL)
            if "api_key" not in openai_kwargs:
                env_key = os.environ.get("PPLX_API_KEY") or os.environ.get(
                    "PERPLEXITY_API_KEY"
                )
                if env_key:
                    openai_kwargs["api_key"] = env_key
            openai_client = AsyncOpenAI(**openai_kwargs)
        self._client = openai_client
        self._builder = _SignedReceiptBuilder(
            deployer_id=deployer_id,
            regulatory_context=regulatory_context or {},
            signer=signer or Ed25519Signer(),
            emitter=emitter or LogEmitter(),
        )
        self.chat = _AsyncChatProxy(self._client.chat, self._builder)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._client, name)
