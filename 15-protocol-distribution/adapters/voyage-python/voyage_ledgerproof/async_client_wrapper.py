"""
Async client wrapper around `voyageai.AsyncClient`. Mirror of client_wrapper.py.
"""

from __future__ import annotations

import logging
from typing import Any

from .client_wrapper import (
    LedgerProofVoyage,
    _coerce_documents,
    _coerce_inputs,
)
from .emitter import Emitter, LogEmitter
from .manual import emit_embedding_receipt, emit_rerank_receipt
from .schema import RegulatoryContext
from .signer import Ed25519Signer, Signer

logger = logging.getLogger(__name__)


class LedgerProofAsyncVoyage(LedgerProofVoyage):
    """
    Async drop-in wrapper for `voyageai.AsyncClient`.

    Usage:
        client = LedgerProofAsyncVoyage(deployer_id="acme-eu", api_key="...")
        result = await client.embed(
            texts=["..."],
            model="voyage-3-large",
            input_type="document",
        )
    """

    def __init__(
        self,
        deployer_id: str,
        *,
        client: Any | None = None,
        signer: Signer | None = None,
        emitter: Emitter | None = None,
        regulatory_context: RegulatoryContext | dict[str, Any] | None = None,
        api_key: str | None = None,
        **voyage_kwargs: Any,
    ):
        # Don't call super().__init__ — it would build a sync voyageai.Client.
        self.deployer_id = deployer_id
        if client is None:
            import voyageai
            client = voyageai.AsyncClient(api_key=api_key, **voyage_kwargs)
        self._inner = client
        self._signer: Signer = signer or Ed25519Signer()
        self._emitter: Emitter = emitter or LogEmitter()
        if isinstance(regulatory_context, dict):
            regulatory_context = RegulatoryContext(**regulatory_context)
        self._reg_ctx: RegulatoryContext | None = regulatory_context

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    # ------------------------------------------------------------------
    # embed() — async
    # ------------------------------------------------------------------
    async def embed(self, *args: Any, **kwargs: Any) -> Any:  # type: ignore[override]
        result = await self._inner.embed(*args, **kwargs)
        try:
            texts = kwargs.get("texts")
            if texts is None and args:
                texts = args[0]
            model = kwargs.get("model")
            if model is None and len(args) >= 2:
                model = args[1]
            input_type = kwargs.get("input_type")
            output_dtype = kwargs.get("output_dtype")

            emit_embedding_receipt(
                deployer_id=self.deployer_id,
                model=str(model) if model is not None else "unknown",
                inputs=_coerce_inputs(texts),
                result=result,
                input_type=input_type,
                output_dtype=output_dtype,
                regulatory_context=self._reg_ctx,
                signer=self._signer,
                emitter=self._emitter,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("LedgerProof async embed receipt emission failed: %s", exc)
        return result

    # ------------------------------------------------------------------
    # rerank() — async
    # ------------------------------------------------------------------
    async def rerank(self, *args: Any, **kwargs: Any) -> Any:  # type: ignore[override]
        result = await self._inner.rerank(*args, **kwargs)
        try:
            query = kwargs.get("query")
            if query is None and args:
                query = args[0]
            documents = kwargs.get("documents")
            if documents is None and len(args) >= 2:
                documents = args[1]
            model = kwargs.get("model")
            if model is None and len(args) >= 3:
                model = args[2]

            emit_rerank_receipt(
                deployer_id=self.deployer_id,
                model=str(model) if model is not None else "unknown",
                query=str(query) if query is not None else "",
                documents=_coerce_documents(documents),
                result=result,
                regulatory_context=self._reg_ctx,
                signer=self._signer,
                emitter=self._emitter,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("LedgerProof async rerank receipt emission failed: %s", exc)
        return result
