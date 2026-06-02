"""Async client wrapper — mirrors `client_wrapper.py` for `openai.AsyncAzureOpenAI`."""

from __future__ import annotations

import hashlib
import uuid
from typing import Any, AsyncIterator

from openai import AsyncAzureOpenAI

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
        azure_deployment: str | None,
    ) -> None:
        self._stream = stream
        self._builder = builder
        self._prompt_sha256 = prompt_sha256
        self._fallback_interaction_id = fallback_interaction_id
        self._azure_deployment = azure_deployment
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
        try:
            self._builder.emit(
                model_id=self._model_id,
                interaction_id=self._interaction_id
                or self._fallback_interaction_id,
                prompt_sha256=self._prompt_sha256,
                response_sha256=self._hasher.hexdigest(),
                azure_deployment=self._azure_deployment,
                extra={"streaming": True},
            )
        except Exception:  # noqa: BLE001
            # C7: receipt failure must never break the caller path
            pass


class _AsyncChatCompletionsProxy:
    def __init__(self, inner: Any, builder: _SignedReceiptBuilder) -> None:
        self._inner = inner
        self._builder = builder

    async def create(self, *args: Any, **kwargs: Any) -> Any:
        messages = kwargs.get("messages")
        prompt_sha256 = _hash_messages(messages)
        streaming = bool(kwargs.get("stream"))
        azure_deployment = kwargs.get("model")
        result = await self._inner.create(*args, **kwargs)

        if streaming:
            return _AsyncStreamingProxy(
                result,
                builder=self._builder,
                prompt_sha256=prompt_sha256,
                fallback_interaction_id=str(uuid.uuid4()),
                azure_deployment=azure_deployment,
            )

        try:
            self._builder.emit(
                model_id=getattr(result, "model", azure_deployment or "unknown"),
                interaction_id=getattr(result, "id", None) or str(uuid.uuid4()),
                prompt_sha256=prompt_sha256,
                response_sha256=_hash_non_streaming_response(result),
                azure_deployment=azure_deployment,
            )
        except Exception:  # noqa: BLE001
            pass
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


class LedgerProofAsyncAzureOpenAI:
    """Async sibling of `LedgerProofAzureOpenAI`."""

    def __init__(
        self,
        deployer_id: str,
        *,
        regulatory_context: dict[str, Any] | None = None,
        signer: Signer | None = None,
        emitter: Emitter | None = None,
        azure_client: AsyncAzureOpenAI | None = None,
        **azure_kwargs: Any,
    ) -> None:
        self._client = azure_client or AsyncAzureOpenAI(**azure_kwargs)

        endpoint = (
            azure_kwargs.get("azure_endpoint")
            or getattr(self._client, "_azure_endpoint", None)
        )
        api_version = azure_kwargs.get("api_version") or getattr(
            self._client, "_api_version", None
        )

        self._builder = _SignedReceiptBuilder(
            deployer_id=deployer_id,
            regulatory_context=regulatory_context or {},
            signer=signer or Ed25519Signer(),
            emitter=emitter or LogEmitter(),
            azure_endpoint=endpoint if isinstance(endpoint, str) else None,
            api_version=api_version if isinstance(api_version, str) else None,
        )
        self.chat = _AsyncChatProxy(self._client.chat, self._builder)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._client, name)
