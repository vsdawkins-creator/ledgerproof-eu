"""
Async client wrapper around `fireworks.client.AsyncFireworks`. Mirror of client_wrapper.py.

Fireworks async SDK reference (fireworks-ai>=0.15):
    from fireworks.client import AsyncFireworks
    client = AsyncFireworks(api_key=...)
    response = await client.chat.completions.acreate(model=..., messages=...)
    async for chunk in client.chat.completions.acreate(..., stream=True):
        ...

Note: The Fireworks Python SDK has historically exposed both `create` and
`acreate` on the async client depending on version. We wrap both names so the
adapter is robust to either.
"""

from __future__ import annotations

import logging
from typing import Any, AsyncIterator

from .canonical import IncrementalTextHasher
from .client_wrapper import (
    LedgerProofFireworks,
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
    def __init__(self, parent: "LedgerProofAsyncFireworks", inner: Any):
        self._parent = parent
        self._inner = inner

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    async def create(self, *args: Any, **kwargs: Any) -> Any:
        stream = bool(kwargs.get("stream"))
        if stream:
            return await self._create_stream(*args, **kwargs)
        return await self._create_blocking(*args, **kwargs)

    # Some Fireworks SDK versions expose `acreate` instead of `create` on the
    # async client. Provide both for compatibility.
    async def acreate(self, *args: Any, **kwargs: Any) -> Any:
        return await self.create(*args, **kwargs)

    async def _create_blocking(self, *args: Any, **kwargs: Any) -> Any:
        target = getattr(self._inner, "acreate", None) or self._inner.create
        response = await target(*args, **kwargs)
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

        target = getattr(self._inner, "acreate", None) or self._inner.create
        inner_iter = await target(*args, **kwargs)

        def _on_finish(last_chunk: Any, h: IncrementalTextHasher) -> None:
            self._parent._emit_for_stream(
                final_chunk=last_chunk,
                user_message_text=user_text,
                text_hasher=h,
            )

        return _AsyncStreamIterator(inner_iter, _on_finish, hasher)


class _AsyncChatProxy:
    def __init__(self, parent: "LedgerProofAsyncFireworks"):
        self._parent = parent
        self._inner = parent._inner.chat

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    @property
    def completions(self) -> _AsyncCompletionsProxy:
        return _AsyncCompletionsProxy(self._parent, self._inner.completions)


class _AsyncImageProxy:
    def __init__(self, parent: "LedgerProofAsyncFireworks"):
        self._parent = parent
        self._inner = parent._inner.image

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    async def generate(self, *args: Any, **kwargs: Any) -> Any:
        target = getattr(self._inner, "agenerate", None) or self._inner.generate
        response = target(*args, **kwargs)
        # Some versions return a coroutine, others a plain value.
        import inspect
        if inspect.isawaitable(response):
            response = await response
        try:
            self._parent._emit_for_image(
                response=response,
                prompt_text=str(kwargs.get("prompt", "")),
                model_hint=str(kwargs.get("model", "")),
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("LedgerProof async FLUX image-receipt emission failed: %s", exc)
        return response


class LedgerProofAsyncFireworks(LedgerProofFireworks):
    """
    Async drop-in wrapper for `fireworks.client.AsyncFireworks`.
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
        **fireworks_kwargs: Any,
    ):
        # Skip the sync super().__init__ default-client path; instantiate the
        # async client lazily.
        self.deployer_id = deployer_id
        self.user_session_id = user_session_id
        if client is None:
            from fireworks.client import AsyncFireworks  # lazy import
            client = AsyncFireworks(**fireworks_kwargs)
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
    def image(self) -> _AsyncImageProxy:  # type: ignore[override]
        return _AsyncImageProxy(self)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)
