"""Async client wrapper — mirrors `client_wrapper.py` for `openai.AsyncOpenAI`."""

from __future__ import annotations

import hashlib
import uuid
from typing import Any, AsyncIterator

from openai import AsyncOpenAI

from .client_wrapper import (
    _SignedReceiptBuilder,
    _extract_chunk_text,
    _hash_messages,
    _hash_non_streaming_response,
)
from .emitter import Emitter, LogEmitter
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

    def _flush(self) -> None:
        if self._emitted:
            return
        self._emitted = True
        self._builder.emit(
            model_id=self._model_id,
            interaction_id=self._interaction_id or self._fallback_interaction_id,
            prompt_sha256=self._prompt_sha256,
            response_sha256=self._hasher.hexdigest(),
            extra={"streaming": True},
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

        self._builder.emit(
            model_id=getattr(result, "model", "unknown"),
            interaction_id=getattr(result, "id", None) or str(uuid.uuid4()),
            prompt_sha256=prompt_sha256,
            response_sha256=_hash_non_streaming_response(result),
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


class LedgerProofAsyncOpenAI:
    """Async sibling of `LedgerProofOpenAI`."""

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
        self._client = openai_client or AsyncOpenAI(**openai_kwargs)
        self._builder = _SignedReceiptBuilder(
            deployer_id=deployer_id,
            regulatory_context=regulatory_context or {},
            signer=signer or Ed25519Signer(),
            emitter=emitter or LogEmitter(),
        )
        self.chat = _AsyncChatProxy(self._client.chat, self._builder)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._client, name)
