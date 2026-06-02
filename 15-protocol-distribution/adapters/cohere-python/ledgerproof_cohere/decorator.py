"""
`@lpr_track` decorator for user functions that wrap a Cohere call.

Use when you already have a function that returns a Cohere ChatResponse and you
want a receipt emitted on each invocation without restructuring your code to use
the client wrapper.
"""

from __future__ import annotations

import asyncio
import functools
import logging
from typing import Any, Callable

from .emitter import Emitter, LogEmitter
from .manual import emit_receipt
from .schema import (
    DisclosureRef,
    RegulatoryContext,
    RetrievedDocumentRef,
    SchemaName,
)
from .signer import Ed25519Signer, Signer

logger = logging.getLogger(__name__)


def lpr_track(
    deployer_id: str,
    *,
    schema: SchemaName = "chatbot_session/v1",
    regulatory_context: RegulatoryContext | dict[str, Any] | None = None,
    signer: Signer | None = None,
    emitter: Emitter | None = None,
    user_message_kwarg: str | None = None,
    retrieved_documents_kwarg: str | None = None,
    disclosure_kwarg: str | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator factory. The wrapped function MUST return a Cohere ChatResponse
    (or anything with `.message.content[*].text`, `.id`, `.model`, `.usage`).

    Args:
        deployer_id: Stable identifier for the deployer (your EU legal entity).
        schema: Receipt schema name. Defaults to chatbot_session/v1.
        regulatory_context: Article 50 metadata (paragraph, jurisdiction, etc.).
        signer: Custom signer (defaults to ephemeral Ed25519).
        emitter: Custom emitter (defaults to LogEmitter).
        user_message_kwarg: Name of a kwarg on the decorated function that holds
            the user message text. If provided and present, its hash is included.
        retrieved_documents_kwarg: Name of a kwarg holding a list of
            RetrievedDocumentRef. If provided, the receipt schema is promoted
            to rag_response/v1.
        disclosure_kwarg: Name of a kwarg holding a DisclosureRef. If provided,
            the receipt schema is promoted to multilingual_disclosure/v1.
    """
    shared_signer = signer or Ed25519Signer()
    shared_emitter = emitter or LogEmitter()

    def _decorate(fn: Callable[..., Any]) -> Callable[..., Any]:
        if asyncio.iscoroutinefunction(fn):

            @functools.wraps(fn)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                result = await fn(*args, **kwargs)
                try:
                    _emit_from_kwargs(
                        result=result,
                        kwargs=kwargs,
                        deployer_id=deployer_id,
                        schema=schema,
                        regulatory_context=regulatory_context,
                        signer=shared_signer,
                        emitter=shared_emitter,
                        user_message_kwarg=user_message_kwarg,
                        retrieved_documents_kwarg=retrieved_documents_kwarg,
                        disclosure_kwarg=disclosure_kwarg,
                    )
                except Exception as exc:  # noqa: BLE001
                    logger.warning("lpr_track receipt emission failed: %s", exc)
                return result

            return async_wrapper

        @functools.wraps(fn)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            result = fn(*args, **kwargs)
            try:
                _emit_from_kwargs(
                    result=result,
                    kwargs=kwargs,
                    deployer_id=deployer_id,
                    schema=schema,
                    regulatory_context=regulatory_context,
                    signer=shared_signer,
                    emitter=shared_emitter,
                    user_message_kwarg=user_message_kwarg,
                    retrieved_documents_kwarg=retrieved_documents_kwarg,
                    disclosure_kwarg=disclosure_kwarg,
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("lpr_track receipt emission failed: %s", exc)
            return result

        return sync_wrapper

    return _decorate


def _emit_from_kwargs(
    *,
    result: Any,
    kwargs: dict[str, Any],
    deployer_id: str,
    schema: SchemaName,
    regulatory_context: RegulatoryContext | dict[str, Any] | None,
    signer: Signer,
    emitter: Emitter,
    user_message_kwarg: str | None,
    retrieved_documents_kwarg: str | None,
    disclosure_kwarg: str | None,
) -> None:
    user_msg = _get_str_kwarg(kwargs, user_message_kwarg)
    retrieved: list[RetrievedDocumentRef] | None = None
    disclosure: DisclosureRef | None = None
    chosen_schema = schema

    if retrieved_documents_kwarg:
        val = kwargs.get(retrieved_documents_kwarg)
        if isinstance(val, list) and all(isinstance(x, RetrievedDocumentRef) for x in val):
            retrieved = val
            chosen_schema = "rag_response/v1"

    if disclosure_kwarg:
        val = kwargs.get(disclosure_kwarg)
        if isinstance(val, DisclosureRef):
            disclosure = val
            chosen_schema = "multilingual_disclosure/v1"

    emit_receipt(
        response=result,
        deployer_id=deployer_id,
        regulatory_context=regulatory_context,
        schema=chosen_schema,
        signer=signer,
        emitter=emitter,
        user_message_text=user_msg,
        retrieved_documents=retrieved,
        disclosure=disclosure,
    )


def _get_str_kwarg(kwargs: dict[str, Any], name: str | None) -> str | None:
    if not name:
        return None
    val = kwargs.get(name)
    return val if isinstance(val, str) else None
