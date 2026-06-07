"""Async client wrapper — mirrors `client_wrapper.py` for `openai.AsyncOpenAI`
pointed at DeepSeek's OpenAI-compatible API.
"""

from __future__ import annotations

import hashlib
import os
import uuid
from typing import Any, AsyncIterator

from openai import AsyncOpenAI

from .client_wrapper import (
    DEEPSEEK_DEFAULT_BASE_URL,
    _SignedReceiptBuilder,
    _extract_chunk_text,
    _extract_response_text_and_reasoning,
    _hash_messages,
    _hash_str,
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
        self._answer_hasher = hashlib.sha256()
        self._reasoning_hasher = hashlib.sha256()
        self._reasoning_seen = False
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
        answer, reasoning = _extract_chunk_text(chunk)
        if answer:
            self._answer_hasher.update(answer.encode("utf-8"))
        if reasoning:
            self._reasoning_seen = True
            self._reasoning_hasher.update(reasoning.encode("utf-8"))

    def _flush(self) -> None:
        if self._emitted:
            return
        self._emitted = True
        schema = self._builder.regulatory_context.get("schema", "chatbot_session/v1")
        extra_fields: dict[str, Any] = {}
        if schema == "reasoning_trace/v1" and self._reasoning_seen:
            extra_fields["reasoning_sha256"] = self._reasoning_hasher.hexdigest()
            extra_fields["trace_surfaced_to_user"] = bool(
                self._builder.regulatory_context.get("trace_surfaced_to_user", False)
            )
        if schema == "code_generation/v1":
            lang = self._builder.regulatory_context.get("programming_language")
            if lang:
                extra_fields["programming_language"] = lang
        self._builder.emit(
            model_id=self._model_id,
            interaction_id=self._interaction_id or self._fallback_interaction_id,
            prompt_sha256=self._prompt_sha256,
            response_sha256=self._answer_hasher.hexdigest(),
            extra={"streaming": True, "provider": "deepseek"},
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
        extra: dict[str, Any] = {"provider": "deepseek"}

        answer_text, reasoning_text = _extract_response_text_and_reasoning(result)

        if schema == "reasoning_trace/v1":
            if reasoning_text:
                extra_fields["reasoning_sha256"] = _hash_str(reasoning_text)
                usage = getattr(result, "usage", None)
                details = getattr(usage, "completion_tokens_details", None) if usage else None
                rtokens = getattr(details, "reasoning_tokens", None) if details else None
                if isinstance(rtokens, int):
                    extra_fields["reasoning_token_count"] = rtokens
            extra_fields["trace_surfaced_to_user"] = bool(
                self._builder.regulatory_context.get("trace_surfaced_to_user", False)
            )

        if schema == "code_generation/v1":
            lang = self._builder.regulatory_context.get("programming_language")
            if lang:
                extra_fields["programming_language"] = lang

        self._builder.emit(
            model_id=getattr(result, "model", "unknown"),
            interaction_id=getattr(result, "id", None) or str(uuid.uuid4()),
            prompt_sha256=prompt_sha256,
            response_sha256=_hash_str(answer_text),
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


class LedgerProofAsyncDeepSeek:
    """Async sibling of `LedgerProofDeepSeek`."""

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
            openai_kwargs.setdefault("base_url", DEEPSEEK_DEFAULT_BASE_URL)
            if "api_key" not in openai_kwargs:
                env_key = os.environ.get("DEEPSEEK_API_KEY")
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
