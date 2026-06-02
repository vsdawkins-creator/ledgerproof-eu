"""
Async client wrapper around `together.AsyncTogether`. Mirror of client_wrapper.py.

Together async SDK reference (together>=1.3):
    from together import AsyncTogether
    client = AsyncTogether(api_key=...)
    response = await client.chat.completions.create(model=..., messages=...)
    async for chunk in await client.chat.completions.create(..., stream=True):
        ...
"""

from __future__ import annotations

import logging
from typing import Any, AsyncIterator

from .canonical import IncrementalTextHasher
from .client_wrapper import (
    LedgerProofTogether,
    _default_reg_ctx,
    _extract_user_message_text,
    _stream_chunk_text,
)
from .emitter import Emitter, LogEmitter
from .schema import OpenModelAttribution, RegulatoryContext, SchemaName
from .signer import Ed25519Signer, Signer

logger = logging.getLogger(__name__)


class _AsyncStreamIterator:
    """Async equivalent of `_StreamIterator` from client_wrapper."""

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
            logger.warning("LedgerProof async streaming receipt failed: %s", exc)

    async def aclose(self) -> None:
        await self._finalize()
        closer = getattr(self._inner, "aclose", None)
        if callable(closer):
            try:
                await closer()
            except Exception:  # noqa: BLE001
                pass


class _AsyncCompletionsProxy:
    def __init__(self, parent: "LedgerProofAsyncTogether", inner: Any):
        self._parent = parent
        self._inner = inner

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    async def create(self, *args: Any, **kwargs: Any) -> Any:
        stream = bool(kwargs.get("stream"))
        if stream:
            return await self._create_stream(*args, **kwargs)
        return await self._create_blocking(*args, **kwargs)

    async def _create_blocking(self, *args: Any, **kwargs: Any) -> Any:
        response = await self._inner.create(*args, **kwargs)
        try:
            self._parent._emit_for_response(
                response=response,
                user_message_text=_extract_user_message_text(kwargs.get("messages")),
                streaming=False,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("LedgerProof receipt emission failed: %s", exc)
        return response

    async def _create_stream(self, *args: Any, **kwargs: Any) -> AsyncIterator[Any]:
        hasher = IncrementalTextHasher()
        user_text = _extract_user_message_text(kwargs.get("messages"))

        inner_iter = await self._inner.create(*args, **kwargs)

        def _on_finish(last_chunk: Any, h: IncrementalTextHasher) -> None:
            self._parent._emit_for_stream(
                final_chunk=last_chunk,
                user_message_text=user_text,
                text_hasher=h,
            )

        return _AsyncStreamIterator(inner_iter, _on_finish, hasher)


class _AsyncChatProxy:
    def __init__(self, parent: "LedgerProofAsyncTogether"):
        self._parent = parent
        self._inner = parent._inner.chat

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    @property
    def completions(self) -> _AsyncCompletionsProxy:
        return _AsyncCompletionsProxy(self._parent, self._inner.completions)


class _AsyncImagesProxy:
    def __init__(self, parent: "LedgerProofAsyncTogether"):
        self._parent = parent
        self._inner = parent._inner.images

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    async def generate(self, *args: Any, **kwargs: Any) -> Any:
        response = await self._inner.generate(*args, **kwargs)
        try:
            self._parent._emit_for_image(
                response=response,
                prompt_text=str(kwargs.get("prompt", "")),
                model_hint=str(kwargs.get("model", "")),
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("LedgerProof async image-receipt emission failed: %s", exc)
        return response


class LedgerProofAsyncTogether(LedgerProofTogether):
    """
    Async drop-in wrapper for `together.AsyncTogether`.
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
        open_model: OpenModelAttribution | dict[str, Any] | None = None,
        user_session_id: str | None = None,
        **together_kwargs: Any,
    ):
        # Skip the sync super().__init__ default-client path; instantiate the
        # async client lazily.
        self.deployer_id = deployer_id
        self.user_session_id = user_session_id
        if client is None:
            from together import AsyncTogether  # lazy import
            client = AsyncTogether(**together_kwargs)
        self._inner = client
        self._signer: Signer = signer or Ed25519Signer()
        self._emitter: Emitter = emitter or LogEmitter()
        self._schema: SchemaName = schema
        if isinstance(regulatory_context, dict):
            regulatory_context = RegulatoryContext(**regulatory_context)
        self._reg_ctx: RegulatoryContext = regulatory_context or _default_reg_ctx()
        if isinstance(open_model, dict):
            open_model = OpenModelAttribution(**open_model)
        self._open_model: OpenModelAttribution | None = open_model

    @property
    def chat(self) -> _AsyncChatProxy:  # type: ignore[override]
        return _AsyncChatProxy(self)

    @property
    def images(self) -> _AsyncImagesProxy:  # type: ignore[override]
        return _AsyncImagesProxy(self)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)
