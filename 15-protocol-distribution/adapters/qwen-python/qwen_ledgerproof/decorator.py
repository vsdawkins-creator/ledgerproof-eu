"""
`@lpr_track` decorator for user functions that wrap a Qwen / DashScope call.

Use when you already have a function that returns a DashScope GenerationResponse
and you want a receipt emitted on each invocation without restructuring your
code to use the client wrapper.
"""

from __future__ import annotations

import asyncio
import functools
import logging
from typing import Any, Callable

from .emitter import Emitter, LogEmitter
from .manual import emit_receipt
from .schema import (
    ChineseInferenceAttestation,
    CrossJurisdictionalRoute,
    RegulatoryContext,
    SchemaName,
)
from .signer import Ed25519Signer, Signer

logger = logging.getLogger(__name__)


def lpr_track(
    deployer_id: str,
    *,
    schema: SchemaName = "chatbot_session/v1",
    regulatory_context: RegulatoryContext | dict[str, Any] | None = None,
    chinese_inference: ChineseInferenceAttestation | dict[str, Any] | None = None,
    cross_jurisdictional_route: CrossJurisdictionalRoute | dict[str, Any] | None = None,
    signer: Signer | None = None,
    emitter: Emitter | None = None,
    user_message_kwarg: str | None = None,
    model_kwarg: str | None = "model",
    user_session_id: str | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator factory. The wrapped function MUST return a DashScope
    GenerationResponse (anything with `.output.text` or
    `.output.choices[0].message.content`, `.request_id`).

    Args:
        deployer_id: Stable identifier for the deployer (your EU legal entity).
        schema: Receipt schema name. Defaults to chatbot_session/v1.
        regulatory_context: Article 50 metadata (paragraph, jurisdiction, etc.).
        chinese_inference: Optional Chinese-origin-AI attestation block.
        cross_jurisdictional_route: Optional cross-jurisdictional-routing
            attestation block.
        signer: Custom signer (defaults to ephemeral Ed25519).
        emitter: Custom emitter (defaults to LogEmitter).
        user_message_kwarg: Name of a kwarg on the decorated function that holds
            the user message text. If provided and present, its hash is included.
        model_kwarg: Name of a kwarg on the decorated function holding the model
            id (used as a fallback because DashScope responses do not always
            echo the model). Defaults to `"model"`.
        user_session_id: Optional opaque session identifier (no PII).
    """
    shared_signer = signer or Ed25519Signer()
    shared_emitter = emitter or LogEmitter()

    def _decorate(fn: Callable[..., Any]) -> Callable[..., Any]:
        if asyncio.iscoroutinefunction(fn):

            @functools.wraps(fn)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                result = await fn(*args, **kwargs)
                try:
                    emit_receipt(
                        response=result,
                        deployer_id=deployer_id,
                        regulatory_context=regulatory_context,
                        schema=schema,
                        signer=shared_signer,
                        emitter=shared_emitter,
                        user_message_text=_get_user_message(kwargs, user_message_kwarg),
                        user_session_id=user_session_id,
                        chinese_inference=chinese_inference,
                        cross_jurisdictional_route=cross_jurisdictional_route,
                        model_id=_get_model_id(kwargs, model_kwarg),
                    )
                except Exception as exc:  # noqa: BLE001
                    logger.warning("lpr_track receipt emission failed: %s", exc)
                return result

            return async_wrapper

        @functools.wraps(fn)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            result = fn(*args, **kwargs)
            try:
                emit_receipt(
                    response=result,
                    deployer_id=deployer_id,
                    regulatory_context=regulatory_context,
                    schema=schema,
                    signer=shared_signer,
                    emitter=shared_emitter,
                    user_message_text=_get_user_message(kwargs, user_message_kwarg),
                    user_session_id=user_session_id,
                    chinese_inference=chinese_inference,
                    cross_jurisdictional_route=cross_jurisdictional_route,
                    model_id=_get_model_id(kwargs, model_kwarg),
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("lpr_track receipt emission failed: %s", exc)
            return result

        return sync_wrapper

    return _decorate


def _get_user_message(kwargs: dict[str, Any], kwarg_name: str | None) -> str | None:
    if not kwarg_name:
        return None
    val = kwargs.get(kwarg_name)
    return val if isinstance(val, str) else None


def _get_model_id(kwargs: dict[str, Any], kwarg_name: str | None) -> str | None:
    if not kwarg_name:
        return None
    val = kwargs.get(kwarg_name)
    return val if isinstance(val, str) else None
