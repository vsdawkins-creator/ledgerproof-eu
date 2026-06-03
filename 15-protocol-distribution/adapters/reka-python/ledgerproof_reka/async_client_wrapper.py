"""
Async client wrapper around `reka.client.AsyncReka`. Mirror of client_wrapper.py.
"""

from __future__ import annotations

import logging
from typing import Any, AsyncIterator

from .canonical import IncrementalTextHasher
from .client_wrapper import (
    LedgerProofReka,  # reuse receipt-building logic
    _default_reg_ctx,
    _extract_media_refs,
    _extract_stream_delta,
    _extract_user_message_text,
)
from .emitter import Emitter, LogEmitter
from .schema import RegulatoryContext, SchemaName
from .signer import Ed25519Signer, Signer

logger = logging.getLogger(__name__)


class _AsyncChatProxy:
    def __init__(self, parent: "LedgerProofAsyncReka"):
        self._parent = parent
        self._inner = parent._inner.chat

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    async def create(self, *args: Any, **kwargs: Any) -> Any:
        response = await self._inner.create(*args, **kwargs)
        try:
            messages = kwargs.get("messages")
            self._parent._emit_for_response(
                response=response,
                user_message_text=_extract_user_message_text(messages),
                media_refs=_extract_media_refs(messages),
                streaming=False,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("LedgerProof receipt emission failed: %s", exc)
        return response

    def create_stream(self, *args: Any, **kwargs: Any) -> "_AsyncStreamIterator":
        """
        Return an async-iterable proxy over Reka's async stream.

        We don't `await` here so callers can use either:
            async for chunk in client.chat.create_stream(...):
                ...
        Or, if Reka returns a coroutine, we await it lazily on first __anext__.
        """
        return _AsyncStreamIterator(
            inner=self._inner.create_stream(*args, **kwargs),
            parent=self._parent,
            messages=kwargs.get("messages"),
        )


class _AsyncStreamIterator:
    def __init__(self, inner: Any, parent: "LedgerProofAsyncReka", messages: Any):
        self._inner = inner
        self._parent = parent
        self._messages = messages
        self._hasher = IncrementalTextHasher()
        self._iterator: AsyncIterator[Any] | None = None
        self._last_chunk: Any = None
        self._finalized = False

    def __aiter__(self):
        return self

    async def __anext__(self) -> Any:
        if self._iterator is None:
            await self._init_iterator()
        try:
            chunk = await self._iterator.__anext__()  # type: ignore[union-attr]
        except StopAsyncIteration:
            self._finalize()
            raise
        delta = _extract_stream_delta(chunk)
        if delta:
            self._hasher.update(delta)
        self._last_chunk = chunk
        return chunk

    async def __aenter__(self):
        await self._init_iterator()
        return self

    async def __aexit__(self, *exc):
        self._finalize()
        return False

    async def _init_iterator(self) -> None:
        if self._iterator is not None:
            return
        obj = self._inner
        # Reka may return a coroutine that resolves to an async iterator.
        if hasattr(obj, "__await__"):
            obj = await obj  # type: ignore[misc]
        if hasattr(obj, "__aiter__"):
            self._iterator = obj.__aiter__()
        else:
            # Fall back to treating it as already an iterator.
            self._iterator = obj  # type: ignore[assignment]

    def _finalize(self) -> None:
        if self._finalized:
            return
        self._finalized = True
        try:
            self._parent._emit_for_stream(
                final_chunk=self._last_chunk,
                user_message_text=_extract_user_message_text(self._messages),
                media_refs=_extract_media_refs(self._messages),
                text_hasher=self._hasher,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("LedgerProof async streaming receipt failed: %s", exc)


class LedgerProofAsyncReka(LedgerProofReka):
    """
    Async drop-in wrapper for `reka.client.AsyncReka`.

    Inherits receipt construction from `LedgerProofReka` but overrides
    `__init__` to wrap an `AsyncReka` instance and `chat` to expose
    the async proxy.
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
        **reka_kwargs: Any,
    ):
        # Don't call super().__init__ — it would build a sync Reka client.
        self.deployer_id = deployer_id
        if client is None:
            from reka.client import AsyncReka  # type: ignore

            client = AsyncReka(**reka_kwargs)
        self._inner = client
        self._signer: Signer = signer or Ed25519Signer()
        self._emitter: Emitter = emitter or LogEmitter()
        self._schema: SchemaName = schema
        if isinstance(regulatory_context, dict):
            regulatory_context = RegulatoryContext(**regulatory_context)
        self._reg_ctx: RegulatoryContext = regulatory_context or _default_reg_ctx()

    @property
    def chat(self) -> _AsyncChatProxy:  # type: ignore[override]
        return _AsyncChatProxy(self)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)
