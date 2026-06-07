"""
Synchronous client wrapper around `voyageai.Client`.

Intercepts `embed()` and `rerank()` to emit a receipt on the side channel
(constraint C7) after the response is materialised. The wrapped Voyage response
object is returned unchanged.

For multimodal embeddings (`multimodal_embed`) and contextualized embeddings
(`contextualized_embed`), all attribute access falls through to the underlying
client via `__getattr__`; only `embed()` and `rerank()` are intercepted in MVP.
"""

from __future__ import annotations

import logging
from typing import Any

from .emitter import Emitter, LogEmitter
from .manual import (
    emit_embedding_receipt,
    emit_rerank_receipt,
)
from .schema import RegulatoryContext
from .signer import Ed25519Signer, Signer

logger = logging.getLogger(__name__)


def _coerce_inputs(texts: Any) -> list[str]:
    """Normalize Voyage embed `texts=` to list[str]."""
    if texts is None:
        return []
    if isinstance(texts, str):
        return [texts]
    return [str(t) for t in texts]


def _coerce_documents(documents: Any) -> list[str]:
    if documents is None:
        return []
    return [str(d) for d in documents]


class LedgerProofVoyage:
    """
    Drop-in wrapper for `voyageai.Client`.

    Usage:
        import voyageai
        from voyage_ledgerproof import LedgerProofVoyage

        client = LedgerProofVoyage(deployer_id="acme-eu", api_key="...")
        result = client.embed(
            texts=["EU AI Act Article 50 text"],
            model="voyage-3-large",
            input_type="document",
        )

    All other attributes/methods of the underlying voyageai.Client are forwarded
    (`multimodal_embed`, `contextualized_embed`, `count_tokens`, etc.).
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
        self.deployer_id = deployer_id
        if client is None:
            import voyageai
            client = voyageai.Client(api_key=api_key, **voyage_kwargs)
        self._inner = client
        self._signer: Signer = signer or Ed25519Signer()
        self._emitter: Emitter = emitter or LogEmitter()
        if isinstance(regulatory_context, dict):
            regulatory_context = RegulatoryContext(**regulatory_context)
        self._reg_ctx: RegulatoryContext | None = regulatory_context

    # ------------------------------------------------------------------
    # Pass-through to the underlying Voyage Client for any non-intercepted attr.
    # ------------------------------------------------------------------
    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    # ------------------------------------------------------------------
    # embed()
    # ------------------------------------------------------------------
    def embed(self, *args: Any, **kwargs: Any) -> Any:
        """
        Wrap `voyageai.Client.embed`. Returns the EmbeddingsObject unchanged.

        Voyage `embed()` signature (positional or keyword):
            embed(texts, model, input_type=None, truncation=None,
                  output_dimension=None, output_dtype=None)
        """
        result = self._inner.embed(*args, **kwargs)
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
            # C7: never break the calling code path.
            logger.warning("LedgerProof embed receipt emission failed: %s", exc)
        return result

    # ------------------------------------------------------------------
    # rerank()
    # ------------------------------------------------------------------
    def rerank(self, *args: Any, **kwargs: Any) -> Any:
        """
        Wrap `voyageai.Client.rerank`. Returns the RerankingObject unchanged.

        Voyage `rerank()` signature:
            rerank(query, documents, model, top_k=None, truncation=None)
        """
        result = self._inner.rerank(*args, **kwargs)
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
            document_ids = kwargs.pop("document_ids", None) if False else None
            # `document_ids` is a LedgerProof-only extension; pull from kwargs
            # without forwarding to Voyage.
            # (We already called Voyage above; safe to inspect kwargs now.)

            emit_rerank_receipt(
                deployer_id=self.deployer_id,
                model=str(model) if model is not None else "unknown",
                query=str(query) if query is not None else "",
                documents=_coerce_documents(documents),
                result=result,
                document_ids=document_ids,
                regulatory_context=self._reg_ctx,
                signer=self._signer,
                emitter=self._emitter,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("LedgerProof rerank receipt emission failed: %s", exc)
        return result
