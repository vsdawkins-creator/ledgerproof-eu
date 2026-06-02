"""Async wrapper for `huggingface_hub.AsyncInferenceClient`.

Mirrors `inference_client_wrapper.py` for the async client. Streaming returns
an async iterator wrapped with stream-aware SHA-256 (constraint **C6**).
"""

from __future__ import annotations

import hashlib
import uuid
from typing import Any, AsyncIterator

from .emitter import Emitter, LogEmitter
from .inference_client_wrapper import (
    _SignedReceiptBuilder,
    _extract_chunk_text,
    _extract_interaction_id,
    _extract_model_id,
    _hash_messages,
    _hash_non_streaming_response,
    _hash_text_prompt,
)
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
        fallback_model_id: str,
    ) -> None:
        self._stream = stream
        self._builder = builder
        self._prompt_sha256 = prompt_sha256
        self._fallback_interaction_id = fallback_interaction_id
        self._hasher = hashlib.sha256()
        self._model_id = fallback_model_id
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
            try:
                await close()
            except Exception:  # noqa: BLE001
                pass

    def _absorb(self, chunk: Any) -> None:
        if self._interaction_id is None:
            self._interaction_id = _extract_interaction_id(chunk)
        self._model_id = _extract_model_id(chunk, self._model_id)
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
                interaction_id=self._interaction_id or self._fallback_interaction_id,
                prompt_sha256=self._prompt_sha256,
                response_sha256=self._hasher.hexdigest(),
                extra={"streaming": True},
            )
        except Exception:  # noqa: BLE001
            pass


class LedgerProofAsyncInferenceClient:
    """Async sibling of `LedgerProofInferenceClient`."""

    def __init__(
        self,
        deployer_id: str,
        *,
        regulatory_context: dict[str, Any] | None = None,
        signer: Signer | None = None,
        emitter: Emitter | None = None,
        inference_client: Any | None = None,
        **hf_kwargs: Any,
    ) -> None:
        if inference_client is None:
            from huggingface_hub import AsyncInferenceClient
            inference_client = AsyncInferenceClient(**hf_kwargs)
        self._client = inference_client
        self._default_model = hf_kwargs.get("model") or getattr(inference_client, "model", None) or "unknown"
        self._builder = _SignedReceiptBuilder(
            deployer_id=deployer_id,
            regulatory_context=regulatory_context or {},
            signer=signer or Ed25519Signer(),
            emitter=emitter or LogEmitter(),
        )

    async def chat_completion(self, *args: Any, **kwargs: Any) -> Any:
        messages = kwargs.get("messages")
        if messages is None and args and isinstance(args[0], list):
            messages = args[0]
        prompt_sha256 = _hash_messages(messages)
        streaming = bool(kwargs.get("stream"))
        model_hint = kwargs.get("model") or self._default_model
        result = await self._client.chat_completion(*args, **kwargs)

        if streaming:
            return _AsyncStreamingProxy(
                result,
                builder=self._builder,
                prompt_sha256=prompt_sha256,
                fallback_interaction_id=str(uuid.uuid4()),
                fallback_model_id=model_hint,
            )

        try:
            self._builder.emit(
                model_id=_extract_model_id(result, model_hint),
                interaction_id=_extract_interaction_id(result) or str(uuid.uuid4()),
                prompt_sha256=prompt_sha256,
                response_sha256=_hash_non_streaming_response(result),
            )
        except Exception:  # noqa: BLE001
            pass
        return result

    async def text_generation(self, prompt: str, *args: Any, **kwargs: Any) -> Any:
        prompt_sha256 = _hash_text_prompt(prompt)
        streaming = bool(kwargs.get("stream"))
        model_hint = kwargs.get("model") or self._default_model
        result = await self._client.text_generation(prompt, *args, **kwargs)

        if streaming:
            return _AsyncStreamingProxy(
                result,
                builder=self._builder,
                prompt_sha256=prompt_sha256,
                fallback_interaction_id=str(uuid.uuid4()),
                fallback_model_id=model_hint,
            )

        try:
            self._builder.emit(
                model_id=_extract_model_id(result, model_hint),
                interaction_id=_extract_interaction_id(result) or str(uuid.uuid4()),
                prompt_sha256=prompt_sha256,
                response_sha256=_hash_non_streaming_response(result),
            )
        except Exception:  # noqa: BLE001
            pass
        return result

    def __getattr__(self, name: str) -> Any:
        return getattr(self._client, name)
