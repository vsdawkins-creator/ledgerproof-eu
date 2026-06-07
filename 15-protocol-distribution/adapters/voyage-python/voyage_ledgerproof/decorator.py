"""
`@lpr_track_embed` / `@lpr_track_rerank` decorators for user functions that wrap
a Voyage embed or rerank call.

Use when you already have a function that returns a Voyage EmbeddingsObject or
RerankingObject and you want a receipt emitted on each invocation without
restructuring your code to use the client wrapper.
"""

from __future__ import annotations

import asyncio
import functools
import logging
from typing import Any, Callable

from .emitter import Emitter, LogEmitter
from .manual import emit_embedding_receipt, emit_rerank_receipt
from .schema import RegulatoryContext
from .signer import Ed25519Signer, Signer

logger = logging.getLogger(__name__)


def lpr_track_embed(
    deployer_id: str,
    *,
    model: str,
    input_type: str | None = None,
    output_dtype: str | None = None,
    inputs_kwarg: str = "texts",
    regulatory_context: RegulatoryContext | dict[str, Any] | None = None,
    signer: Signer | None = None,
    emitter: Emitter | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator factory for embed-shaped functions.

    The wrapped function MUST return a Voyage EmbeddingsObject (or equivalent
    with `.embeddings: List[List[float]]` and optional `.total_tokens`).
    """
    shared_signer = signer or Ed25519Signer()
    shared_emitter = emitter or LogEmitter()

    def _decorate(fn: Callable[..., Any]) -> Callable[..., Any]:
        if asyncio.iscoroutinefunction(fn):

            @functools.wraps(fn)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                result = await fn(*args, **kwargs)
                try:
                    inputs = _coerce_list(kwargs.get(inputs_kwarg))
                    emit_embedding_receipt(
                        deployer_id=deployer_id,
                        model=model,
                        inputs=inputs,
                        result=result,
                        input_type=input_type,
                        output_dtype=output_dtype,
                        regulatory_context=regulatory_context,
                        signer=shared_signer,
                        emitter=shared_emitter,
                    )
                except Exception as exc:  # noqa: BLE001
                    logger.warning("lpr_track_embed receipt emission failed: %s", exc)
                return result

            return async_wrapper

        @functools.wraps(fn)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            result = fn(*args, **kwargs)
            try:
                inputs = _coerce_list(kwargs.get(inputs_kwarg))
                emit_embedding_receipt(
                    deployer_id=deployer_id,
                    model=model,
                    inputs=inputs,
                    result=result,
                    input_type=input_type,
                    output_dtype=output_dtype,
                    regulatory_context=regulatory_context,
                    signer=shared_signer,
                    emitter=shared_emitter,
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("lpr_track_embed receipt emission failed: %s", exc)
            return result

        return sync_wrapper

    return _decorate


def lpr_track_rerank(
    deployer_id: str,
    *,
    model: str,
    query_kwarg: str = "query",
    documents_kwarg: str = "documents",
    regulatory_context: RegulatoryContext | dict[str, Any] | None = None,
    signer: Signer | None = None,
    emitter: Emitter | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator factory for rerank-shaped functions."""
    shared_signer = signer or Ed25519Signer()
    shared_emitter = emitter or LogEmitter()

    def _decorate(fn: Callable[..., Any]) -> Callable[..., Any]:
        if asyncio.iscoroutinefunction(fn):

            @functools.wraps(fn)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                result = await fn(*args, **kwargs)
                try:
                    query = str(kwargs.get(query_kwarg) or "")
                    docs = _coerce_list(kwargs.get(documents_kwarg))
                    emit_rerank_receipt(
                        deployer_id=deployer_id,
                        model=model,
                        query=query,
                        documents=docs,
                        result=result,
                        regulatory_context=regulatory_context,
                        signer=shared_signer,
                        emitter=shared_emitter,
                    )
                except Exception as exc:  # noqa: BLE001
                    logger.warning("lpr_track_rerank receipt emission failed: %s", exc)
                return result

            return async_wrapper

        @functools.wraps(fn)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            result = fn(*args, **kwargs)
            try:
                query = str(kwargs.get(query_kwarg) or "")
                docs = _coerce_list(kwargs.get(documents_kwarg))
                emit_rerank_receipt(
                    deployer_id=deployer_id,
                    model=model,
                    query=query,
                    documents=docs,
                    result=result,
                    regulatory_context=regulatory_context,
                    signer=shared_signer,
                    emitter=shared_emitter,
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("lpr_track_rerank receipt emission failed: %s", exc)
            return result

        return sync_wrapper

    return _decorate


def _coerce_list(v: Any) -> list[str]:
    if v is None:
        return []
    if isinstance(v, str):
        return [v]
    return [str(x) for x in v]
