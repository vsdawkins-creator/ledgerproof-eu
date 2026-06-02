"""Async ``AsyncClient`` wrapper for the Aleph Alpha SDK."""

from __future__ import annotations

from typing import Any, Mapping, Optional

from .client_wrapper import (
    _completion_text_of,
    _model_version_of,
    _prompt_text_of,
)
from .emitter import Emitter, StdoutEmitter
from .manual import emit_receipt
from .signer import EphemeralEd25519Signer


class LedgerProofAsyncAlephAlpha:
    """Async wrapper around ``aleph_alpha_client.AsyncClient``.

    Mirrors the sync wrapper's contract: response payload is forwarded
    unmodified (C7); receipts are emitted side-channel.
    """

    def __init__(
        self,
        upstream: Any,
        *,
        article: str = "50(2)",
        schema: str = "generated_content/v1",
        deployer_id: Optional[str] = None,
        extra: Optional[Mapping[str, Any]] = None,
        emitter: Optional[Emitter] = None,
        signer: Optional[EphemeralEd25519Signer] = None,
    ) -> None:
        self._upstream = upstream
        self._article = article
        self._schema = schema
        self._deployer_id = deployer_id
        self._extra = dict(extra or {})
        self._emitter = emitter if emitter is not None else StdoutEmitter()
        self._signer = signer if signer is not None else EphemeralEd25519Signer()

    async def complete(self, request: Any, model: str, **kwargs: Any) -> Any:
        response = await self._upstream.complete(request, model=model, **kwargs)
        self._emit_for(request, response, model)
        return response

    async def __aenter__(self) -> "LedgerProofAsyncAlephAlpha":
        if hasattr(self._upstream, "__aenter__"):
            await self._upstream.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if hasattr(self._upstream, "__aexit__"):
            await self._upstream.__aexit__(exc_type, exc, tb)

    def __getattr__(self, item: str) -> Any:
        return getattr(self._upstream, item)

    def _emit_for(self, request: Any, response: Any, model: str) -> None:
        extra: dict[str, Any] = dict(self._extra)
        if self._deployer_id and "deployer_id" not in extra and self._schema in (
            "chatbot_session/v1",
            "generated_content/v1",
        ):
            extra["deployer_id"] = self._deployer_id
        emit_receipt(
            article=self._article,
            schema=self._schema,
            prompt_text=_prompt_text_of(request),
            completion_text=_completion_text_of(response),
            model=model,
            model_version=_model_version_of(response),
            extra=extra,
            signer=self._signer,
            emitter=self._emitter,
        )
