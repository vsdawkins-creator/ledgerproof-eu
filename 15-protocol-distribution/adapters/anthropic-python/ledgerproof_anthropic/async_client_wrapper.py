"""
Async client wrapper around `anthropic.AsyncAnthropic`. Mirror of client_wrapper.py.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from anthropic import AsyncAnthropic

from .canonical import IncrementalTextHasher
from .client_wrapper import (
    LedgerProofAnthropic,  # reuse receipt-building logic
    _default_reg_ctx,
    _extract_user_message_text,
)
from .emitter import Emitter, LogEmitter
from .schema import RegulatoryContext, SchemaName
from .signer import Ed25519Signer, Signer

logger = logging.getLogger(__name__)


class _AsyncMessagesProxy:
    def __init__(self, parent: "LedgerProofAsyncAnthropic"):
        self._parent = parent
        self._inner = parent._inner.messages

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    async def create(self, *args: Any, **kwargs: Any) -> Any:
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

    @asynccontextmanager
    async def stream(self, *args: Any, **kwargs: Any) -> AsyncIterator[Any]:
        hasher = IncrementalTextHasher()
        user_text = _extract_user_message_text(kwargs.get("messages"))

        async with self._inner.stream(*args, **kwargs) as inner_stream:
            wrapped = _AsyncStreamWrapper(inner_stream, hasher)
            try:
                yield wrapped
            finally:
                try:
                    final_message = await wrapped.get_final_message_safe()
                    self._parent._emit_for_stream(
                        final_message=final_message,
                        user_message_text=user_text,
                        text_hasher=hasher,
                    )
                except Exception as exc:  # noqa: BLE001
                    logger.warning("LedgerProof async streaming receipt failed: %s", exc)


class _AsyncStreamWrapper:
    def __init__(self, inner: Any, hasher: IncrementalTextHasher):
        self._inner = inner
        self._hasher = hasher

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    @property
    def text_stream(self) -> AsyncIterator[str]:
        return self._wrap_text_stream()

    async def _wrap_text_stream(self) -> AsyncIterator[str]:
        async for delta in self._inner.text_stream:
            self._hasher.update(delta)
            yield delta

    async def get_final_message_safe(self) -> Any:
        try:
            return await self._inner.get_final_message()
        except Exception:
            return None


class LedgerProofAsyncAnthropic(LedgerProofAnthropic):
    """
    Async drop-in wrapper for `anthropic.AsyncAnthropic`.

    Inherits receipt construction from `LedgerProofAnthropic` but overrides
    `__init__` to wrap an `AsyncAnthropic` instance and `messages` to expose
    the async proxy.
    """

    def __init__(
        self,
        deployer_id: str,
        *,
        client: AsyncAnthropic | None = None,
        signer: Signer | None = None,
        emitter: Emitter | None = None,
        regulatory_context: RegulatoryContext | dict[str, Any] | None = None,
        schema: SchemaName = "chatbot_session/v1",
        **anthropic_kwargs: Any,
    ):
        # Don't call super().__init__ — it would build a sync Anthropic client.
        self.deployer_id = deployer_id
        self._inner: AsyncAnthropic = client or AsyncAnthropic(**anthropic_kwargs)
        self._signer: Signer = signer or Ed25519Signer()
        self._emitter: Emitter = emitter or LogEmitter()
        self._schema: SchemaName = schema
        if isinstance(regulatory_context, dict):
            regulatory_context = RegulatoryContext(**regulatory_context)
        self._reg_ctx: RegulatoryContext = regulatory_context or _default_reg_ctx()

    @property
    def messages(self) -> _AsyncMessagesProxy:  # type: ignore[override]
        return _AsyncMessagesProxy(self)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)
