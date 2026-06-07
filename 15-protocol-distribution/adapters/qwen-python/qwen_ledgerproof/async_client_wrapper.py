"""
Async client wrapper around DashScope's `AioGeneration` interface.

DashScope SDK reference (dashscope>=1.20):
    from dashscope.aigc.generation import AioGeneration

    response = await AioGeneration.call(model="qwen-max", messages=[...])
    async for chunk in await AioGeneration.call(..., stream=True):
        ...
"""

from __future__ import annotations

import logging
from typing import Any, AsyncIterator

from .canonical import IncrementalTextHasher
from .client_wrapper import (
    LedgerProofQwen,
    _default_reg_ctx,
    _extract_user_message_text,
    _stream_chunk_text,
)
from .emitter import Emitter, LogEmitter
from .schema import (
    ChineseInferenceAttestation,
    CrossJurisdictionalRoute,
    RegulatoryContext,
    SchemaName,
)
from .signer import Ed25519Signer, Signer

logger = logging.getLogger(__name__)


class _AsyncStreamIterator:
    """Async equivalent of `_StreamIterator` from client_wrapper."""

    def __init__(self, inner: AsyncIterator[Any], on_finish, hasher: IncrementalTextHasher):
        self._inner = inner
        self._on_finish = on_finish
        self._hasher = hasher
        self._prev_cumulative = ""
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
        chunk_text = _stream_chunk_text(chunk)
        if chunk_text:
            if chunk_text == self._prev_cumulative:
                pass
            elif chunk_text.startswith(self._prev_cumulative):
                delta = chunk_text[len(self._prev_cumulative) :]
                self._hasher.update(delta)
                self._prev_cumulative = chunk_text
            elif self._prev_cumulative == "":
                self._hasher.update(chunk_text)
                self._prev_cumulative = chunk_text
            else:
                self._hasher.update(chunk_text)
                self._prev_cumulative += chunk_text
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


class _AsyncGenerationProxy:
    def __init__(self, parent: "LedgerProofAsyncQwen", inner: Any):
        self._parent = parent
        self._inner = inner

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    async def call(self, *args: Any, **kwargs: Any) -> Any:
        model_id: str | None = kwargs.get("model") or (args[0] if args else None)
        messages = kwargs.get("messages")
        prompt = kwargs.get("prompt")
        user_text = _extract_user_message_text(messages, prompt)
        streaming = bool(kwargs.get("stream"))

        result = await self._inner.call(*args, **kwargs)

        if streaming:
            hasher = IncrementalTextHasher()

            def _on_finish(last_chunk: Any, h: IncrementalTextHasher) -> None:
                self._parent._emit_for_stream(
                    final_chunk=last_chunk,
                    user_message_text=user_text,
                    text_hasher=h,
                    model_id=model_id,
                )

            return _AsyncStreamIterator(result, _on_finish, hasher)

        try:
            self._parent._emit_for_response(
                response=result,
                user_message_text=user_text,
                streaming=False,
                model_id=model_id,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("LedgerProof receipt emission failed: %s", exc)
        return result


class LedgerProofAsyncQwen(LedgerProofQwen):
    """
    Async drop-in wrapper for DashScope's `AioGeneration`.

    Inherits receipt construction from `LedgerProofQwen` but overrides
    `__init__` to import `AioGeneration` instead of `Generation`, and exposes
    the async proxy under `.generation`.
    """

    def __init__(
        self,
        deployer_id: str,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        generation: Any | None = None,
        signer: Signer | None = None,
        emitter: Emitter | None = None,
        regulatory_context: RegulatoryContext | dict[str, Any] | None = None,
        schema: SchemaName = "chatbot_session/v1",
        chinese_inference: ChineseInferenceAttestation | dict[str, Any] | None = None,
        cross_jurisdictional_route: CrossJurisdictionalRoute | dict[str, Any] | None = None,
        user_session_id: str | None = None,
    ):
        self.deployer_id = deployer_id
        self.user_session_id = user_session_id

        if generation is None:
            import dashscope
            from dashscope.aigc.generation import AioGeneration

            if api_key is not None:
                dashscope.api_key = api_key
            if base_url is not None:
                dashscope.base_http_api_url = base_url
            generation = AioGeneration

        self._generation = generation
        self._signer: Signer = signer or Ed25519Signer()
        self._emitter: Emitter = emitter or LogEmitter()
        self._schema: SchemaName = schema
        if isinstance(regulatory_context, dict):
            regulatory_context = RegulatoryContext(**regulatory_context)
        self._reg_ctx: RegulatoryContext = regulatory_context or _default_reg_ctx()
        if isinstance(chinese_inference, dict):
            chinese_inference = ChineseInferenceAttestation(**chinese_inference)
        self._chinese: ChineseInferenceAttestation | None = chinese_inference
        if isinstance(cross_jurisdictional_route, dict):
            cross_jurisdictional_route = CrossJurisdictionalRoute(**cross_jurisdictional_route)
        self._cjr: CrossJurisdictionalRoute | None = cross_jurisdictional_route

    @property
    def generation(self) -> _AsyncGenerationProxy:  # type: ignore[override]
        return _AsyncGenerationProxy(self, self._generation)
