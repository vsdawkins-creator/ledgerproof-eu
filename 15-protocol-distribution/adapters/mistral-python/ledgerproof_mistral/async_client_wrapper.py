"""
Async client wrapper around `mistralai.Mistral`. Mirror of client_wrapper.py.

Mistral SDK reference (mistralai>=1.0):
    response = await client.chat.complete_async(model=..., messages=...)
    async for chunk in await client.chat.stream_async(...):
        ...
"""

from __future__ import annotations

import logging
from typing import Any, AsyncIterator

from .canonical import IncrementalTextHasher
from .client_wrapper import (
    LedgerProofMistral,
    _default_reg_ctx,
    _extract_user_message_text,
    _stream_chunk_text,
)
from .emitter import Emitter, LogEmitter
from .schema import EuSovereigntyAttestation, RegulatoryContext, SchemaName
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


class _AsyncChatProxy:
    def __init__(self, parent: "LedgerProofAsyncMistral"):
        self._parent = parent
        self._inner = parent._inner.chat

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    async def complete_async(self, *args: Any, **kwargs: Any) -> Any:
        response = await self._inner.complete_async(*args, **kwargs)
        try:
            self._parent._emit_for_response(
                response=response,
                user_message_text=_extract_user_message_text(kwargs.get("messages")),
                streaming=False,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("LedgerProof receipt emission failed: %s", exc)
        return response

    async def stream_async(self, *args: Any, **kwargs: Any) -> AsyncIterator[Any]:
        hasher = IncrementalTextHasher()
        user_text = _extract_user_message_text(kwargs.get("messages"))

        inner_iter = await self._inner.stream_async(*args, **kwargs)

        def _on_finish(last_chunk: Any, h: IncrementalTextHasher) -> None:
            self._parent._emit_for_stream(
                final_chunk=last_chunk,
                user_message_text=user_text,
                text_hasher=h,
            )

        return _AsyncStreamIterator(inner_iter, _on_finish, hasher)


class LedgerProofAsyncMistral(LedgerProofMistral):
    """
    Async drop-in wrapper for `mistralai.Mistral`.

    Inherits receipt construction from `LedgerProofMistral` but overrides
    `__init__` to skip the sync default-client construction, and `chat` to
    expose the async proxy.
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
        eu_sovereignty: EuSovereigntyAttestation | dict[str, Any] | None = None,
        user_session_id: str | None = None,
        **mistral_kwargs: Any,
    ):
        # Don't call super().__init__ verbatim — we still want a Mistral client,
        # but the Mistral SDK uses the SAME class for sync & async (it routes
        # internally based on whether you call `complete` vs `complete_async`).
        self.deployer_id = deployer_id
        self.user_session_id = user_session_id
        if client is None:
            from mistralai import Mistral  # lazy import
            client = Mistral(**mistral_kwargs)
        self._inner = client
        self._signer: Signer = signer or Ed25519Signer()
        self._emitter: Emitter = emitter or LogEmitter()
        self._schema: SchemaName = schema
        if isinstance(regulatory_context, dict):
            regulatory_context = RegulatoryContext(**regulatory_context)
        self._reg_ctx: RegulatoryContext = regulatory_context or _default_reg_ctx()
        if isinstance(eu_sovereignty, dict):
            eu_sovereignty = EuSovereigntyAttestation(**eu_sovereignty)
        self._eu_sov: EuSovereigntyAttestation | None = eu_sovereignty

    @property
    def chat(self) -> _AsyncChatProxy:  # type: ignore[override]
        return _AsyncChatProxy(self)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)
