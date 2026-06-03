"""
Async client wrapper around `mistralai.Mistral` pointed at the Codestral endpoint.
Mirrors codestral_wrapper.py for `complete_async` / `stream_async` paths on both
chat and FIM.

Mistral SDK reference (mistralai>=1.0, Codestral endpoint):
    response = await client.chat.complete_async(model=..., messages=...)
    async for chunk in await client.chat.stream_async(...): ...
    response = await client.fim.complete_async(model=..., prompt=..., suffix=...)
    async for chunk in await client.fim.stream_async(...): ...
"""

from __future__ import annotations

import logging
import os
from typing import Any, AsyncIterator

from .canonical import IncrementalTextHasher
from .codestral_wrapper import (
    DEFAULT_CODESTRAL_URL,
    LedgerProofCodestral,
    _extract_user_message_text,
    _stream_chunk_text,
)
from .emitter import Emitter, LogEmitter
from .schema import RegulatoryContext, SchemaName
from .signer import Ed25519Signer, Signer

logger = logging.getLogger(__name__)


class _AsyncStreamIterator:
    """Async equivalent of `_StreamIterator` from codestral_wrapper."""

    def __init__(self, inner: AsyncIterator[Any], on_finish, hasher: IncrementalTextHasher):
        self._inner = inner
        self._on_finish = on_finish
        self._hasher = hasher
        self._last_chunk: Any = None
        self._finished = False

    def __aiter__(self) -> "_AsyncStreamIterator":
        return self

    async def __anext__(self) -> Any:
        try:
            chunk = await self._inner.__anext__()
        except StopAsyncIteration:
            await self._finalize()
            raise
        text = _stream_chunk_text(chunk)
        if text:
            self._hasher.update(text)
        self._last_chunk = chunk
        return chunk

    async def _finalize(self) -> None:
        if self._finished:
            return
        self._finished = True
        try:
            self._on_finish(self._last_chunk, self._hasher)
        except Exception as exc:  # noqa: BLE001
            logger.warning("LedgerProof Codestral async streaming receipt failed: %s", exc)

    async def aclose(self) -> None:
        await self._finalize()
        closer = getattr(self._inner, "aclose", None)
        if callable(closer):
            try:
                await closer()
            except Exception:  # noqa: BLE001
                pass


class _AsyncChatProxy:
    def __init__(self, parent: "LedgerProofAsyncCodestral"):
        self._parent = parent
        self._inner = parent._inner.chat

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    async def complete_async(self, *args: Any, **kwargs: Any) -> Any:
        response = await self._inner.complete_async(*args, **kwargs)
        try:
            self._parent._emit_for_chat_response(
                response=response,
                user_message_text=_extract_user_message_text(kwargs.get("messages")),
                streaming=False,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("LedgerProof Codestral receipt emission failed: %s", exc)
        return response

    async def stream_async(self, *args: Any, **kwargs: Any) -> AsyncIterator[Any]:
        hasher = IncrementalTextHasher()
        user_text = _extract_user_message_text(kwargs.get("messages"))
        inner_iter = await self._inner.stream_async(*args, **kwargs)

        def _on_finish(last_chunk: Any, h: IncrementalTextHasher) -> None:
            self._parent._emit_for_chat_stream(
                final_chunk=last_chunk,
                user_message_text=user_text,
                text_hasher=h,
            )

        return _AsyncStreamIterator(inner_iter, _on_finish, hasher)


class _AsyncFimProxy:
    def __init__(self, parent: "LedgerProofAsyncCodestral"):
        self._parent = parent
        self._inner = parent._inner.fim

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    async def complete_async(self, *args: Any, **kwargs: Any) -> Any:
        response = await self._inner.complete_async(*args, **kwargs)
        try:
            self._parent._emit_for_fim_response(
                response=response,
                prompt=kwargs.get("prompt", "") or "",
                suffix=kwargs.get("suffix", "") or "",
                streaming=False,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("LedgerProof Codestral FIM receipt emission failed: %s", exc)
        return response

    async def stream_async(self, *args: Any, **kwargs: Any) -> AsyncIterator[Any]:
        hasher = IncrementalTextHasher()
        prompt = kwargs.get("prompt", "") or ""
        suffix = kwargs.get("suffix", "") or ""
        inner_iter = await self._inner.stream_async(*args, **kwargs)

        def _on_finish(last_chunk: Any, h: IncrementalTextHasher) -> None:
            self._parent._emit_for_fim_stream(
                final_chunk=last_chunk,
                prompt=prompt,
                suffix=suffix,
                text_hasher=h,
            )

        return _AsyncStreamIterator(inner_iter, _on_finish, hasher)


class LedgerProofAsyncCodestral(LedgerProofCodestral):
    """
    Async drop-in wrapper for `mistralai.Mistral` against the Codestral endpoint.

    Inherits receipt construction from `LedgerProofCodestral` but overrides
    `__init__` to skip the sync default-client construction, and `chat` / `fim`
    to expose the async proxies.
    """

    def __init__(
        self,
        deployer_id: str,
        *,
        client: Any | None = None,
        signer: Signer | None = None,
        emitter: Emitter | None = None,
        regulatory_context: RegulatoryContext | dict[str, Any] | None = None,
        chat_schema: SchemaName = "generated_code/v1",
        fim_schema: SchemaName = "fim_completion/v1",
        language: str = "unknown",
        user_session_id: str | None = None,
        api_key: str | None = None,
        server_url: str = DEFAULT_CODESTRAL_URL,
        **mistral_kwargs: Any,
    ):
        self.deployer_id = deployer_id
        self.user_session_id = user_session_id
        self._language = (language or "unknown").lower()
        if client is None:
            from mistralai import Mistral  # lazy import
            api_key = api_key or os.environ.get("MISTRAL_CODESTRAL_API_KEY")
            client = Mistral(api_key=api_key, server_url=server_url, **mistral_kwargs)
        self._inner = client
        self._signer: Signer = signer or Ed25519Signer()
        self._emitter: Emitter = emitter or LogEmitter()
        self._chat_schema: SchemaName = chat_schema
        self._fim_schema: SchemaName = fim_schema
        if isinstance(regulatory_context, dict):
            regulatory_context = RegulatoryContext(**regulatory_context)
        self._reg_ctx_override: RegulatoryContext | None = regulatory_context

    @property
    def chat(self) -> _AsyncChatProxy:  # type: ignore[override]
        return _AsyncChatProxy(self)

    @property
    def fim(self) -> _AsyncFimProxy:  # type: ignore[override]
        return _AsyncFimProxy(self)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)
