"""
`@lpr_track` decorator for user functions that wrap a Replicate call.

Use when you already have a function that calls `replicate.run(...)` (or
`client.predictions.create(...)`) and you want a receipt emitted on each
invocation without restructuring your code to use the client wrapper.

The decorated function MUST return either:
  - the Replicate output value, with the model coordinate passed as a kwarg
    (default: `model_ref_kwarg="ref"`), OR
  - a tuple `(model_coordinate_string, output, inputs_dict)` for full control.
"""

from __future__ import annotations

import asyncio
import functools
import logging
from typing import Any, Callable

from .canonical import hash_text
from .client_wrapper import _classify_output
from .emitter import Emitter, LogEmitter
from .manual import build_input_refs, build_model_ref_from_coordinate, emit_receipt
from .schema import RegulatoryContext, SchemaName
from .signer import Ed25519Signer, Signer

logger = logging.getLogger(__name__)


def lpr_track(
    deployer_id: str,
    *,
    schema: SchemaName | None = None,
    regulatory_context: RegulatoryContext | dict[str, Any] | None = None,
    signer: Signer | None = None,
    emitter: Emitter | None = None,
    model_ref_kwarg: str = "ref",
    input_kwarg: str = "input",
    prompt_text_kwarg: str | None = "prompt",
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator factory. Emits a LedgerProof receipt every time the wrapped
    function returns.

    Args:
        deployer_id: Stable identifier for the deployer (your EU legal entity).
        schema: Optional explicit schema. If None, inferred from the output.
        regulatory_context: Article 50 metadata.
        signer: Custom signer (defaults to ephemeral Ed25519).
        emitter: Custom emitter (defaults to LogEmitter).
        model_ref_kwarg: Name of the kwarg holding the Replicate model
            coordinate (e.g. `ref="black-forest-labs/flux-schnell"`).
        input_kwarg: Name of the kwarg holding the input dict.
        prompt_text_kwarg: Name of the field inside the input dict whose value
            is the user prompt (defaults to "prompt"; set None to disable).
    """
    shared_signer = signer or Ed25519Signer()
    shared_emitter = emitter or LogEmitter()

    def _decorate(fn: Callable[..., Any]) -> Callable[..., Any]:
        if asyncio.iscoroutinefunction(fn):

            @functools.wraps(fn)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                result = await fn(*args, **kwargs)
                try:
                    _emit_from_call(
                        result=result,
                        kwargs=kwargs,
                        deployer_id=deployer_id,
                        schema=schema,
                        regulatory_context=regulatory_context,
                        signer=shared_signer,
                        emitter=shared_emitter,
                        model_ref_kwarg=model_ref_kwarg,
                        input_kwarg=input_kwarg,
                        prompt_text_kwarg=prompt_text_kwarg,
                    )
                except Exception as exc:  # noqa: BLE001
                    logger.warning("lpr_track receipt emission failed: %s", exc)
                return result

            return async_wrapper

        @functools.wraps(fn)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            result = fn(*args, **kwargs)
            try:
                _emit_from_call(
                    result=result,
                    kwargs=kwargs,
                    deployer_id=deployer_id,
                    schema=schema,
                    regulatory_context=regulatory_context,
                    signer=shared_signer,
                    emitter=shared_emitter,
                    model_ref_kwarg=model_ref_kwarg,
                    input_kwarg=input_kwarg,
                    prompt_text_kwarg=prompt_text_kwarg,
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("lpr_track receipt emission failed: %s", exc)
            return result

        return sync_wrapper

    return _decorate


def _emit_from_call(
    *,
    result: Any,
    kwargs: dict[str, Any],
    deployer_id: str,
    schema: SchemaName | None,
    regulatory_context: RegulatoryContext | dict[str, Any] | None,
    signer: Signer,
    emitter: Emitter,
    model_ref_kwarg: str,
    input_kwarg: str,
    prompt_text_kwarg: str | None,
) -> None:
    # Allow callers to return (ref, output, inputs) for full control.
    if isinstance(result, tuple) and len(result) == 3 and isinstance(result[0], str):
        ref, output, inputs = result
    else:
        ref = kwargs.get(model_ref_kwarg)
        if not isinstance(ref, str):
            logger.warning(
                "lpr_track: could not find model ref kwarg %r; skipping receipt",
                model_ref_kwarg,
            )
            return
        inputs = kwargs.get(input_kwarg) or {}
        output = result

    prompt_text = None
    if prompt_text_kwarg and isinstance(inputs, dict):
        v = inputs.get(prompt_text_kwarg)
        if isinstance(v, str):
            prompt_text = v

    content_refs, artifacts, inferred_schema = _classify_output(output, prompt_text=prompt_text)
    chosen_schema = schema or inferred_schema or "generated_content/v1"

    model_ref = build_model_ref_from_coordinate(
        ref,
        prediction_id="decorated-call",
        status="succeeded",
    )

    # Delegate to emit_receipt with pre-computed refs.
    import base64
    import uuid

    from .canonical import canonical_encode
    from .schema import ReceiptV1
    from .version import __version__

    if regulatory_context is None:
        from .manual import _default_regulatory_context
        regulatory_context = _default_regulatory_context()
    elif isinstance(regulatory_context, dict):
        regulatory_context = RegulatoryContext(**regulatory_context)

    receipt = ReceiptV1(
        schema=chosen_schema,
        receipt_id=str(uuid.uuid4()),
        deployer_id=deployer_id,
        model=model_ref,
        content_refs=content_refs,
        input_refs=build_input_refs(inputs) if isinstance(inputs, dict) else [],
        output_artifacts=artifacts,
        regulatory_context=regulatory_context,
        streaming=False,
        adapter_version=__version__,
    )
    payload = receipt.to_payload()
    canonical_bytes = canonical_encode(payload)
    signature = signer.sign(canonical_bytes)
    signed = {
        "receipt": payload,
        "signature_alg": "ed25519",
        "signature_b64": base64.b64encode(signature).decode("ascii"),
        "signer_key_id": signer.key_id,
        "canonical_encoding": "cbor-rfc8949-deterministic",
    }
    emitter.emit(signed)
