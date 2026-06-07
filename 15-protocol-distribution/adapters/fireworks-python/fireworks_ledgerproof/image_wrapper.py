"""
Standalone helper for Fireworks FLUX image generation outside the
LedgerProofFireworks client wrapper.

Use when the caller already holds a Fireworks client and just wants to wrap a
single `client.image.generate(...)` call with a receipt.

Example:
    from fireworks.client import Fireworks
    from fireworks_ledgerproof.image_wrapper import generate_flux_with_receipt

    fw = Fireworks(api_key="fw_...")
    image, signed = generate_flux_with_receipt(
        client=fw,
        deployer_id="acme-eu",
        model="accounts/fireworks/models/flux-1-schnell-fp8",
        prompt="A photograph of an alpine lake at sunrise.",
    )
"""

from __future__ import annotations

import logging
from typing import Any

from .client_wrapper import _extract_image_bytes
from .emitter import Emitter
from .manual import emit_flux_image_generation_receipt
from .schema import OpenModelAttribution, RegulatoryContext
from .signer import Signer

logger = logging.getLogger(__name__)


def generate_flux_with_receipt(
    *,
    client: Any,
    deployer_id: str,
    model: str,
    prompt: str,
    signer: Signer | None = None,
    emitter: Emitter | None = None,
    open_model: OpenModelAttribution | dict[str, Any] | None = None,
    regulatory_context: RegulatoryContext | dict[str, Any] | None = None,
    user_session_id: str | None = None,
    **image_kwargs: Any,
) -> tuple[Any, dict[str, Any]]:
    """
    Call Fireworks's FLUX image endpoint and emit a flux_image_generation/v1
    receipt on the side channel.

    Returns:
        (response, signed_receipt)

    The response is returned UNCHANGED (constraint C7). The signed receipt is
    additionally returned for inspection; it is NOT injected into `response`.

    If receipt construction fails, the response is still returned and the
    `signed_receipt` dict will be empty (best-effort, never breaks the call).
    """
    response = client.image.generate(model=model, prompt=prompt, **image_kwargs)
    signed: dict[str, Any] = {}
    try:
        image_blobs = _extract_image_bytes(response)
        signed = emit_flux_image_generation_receipt(
            response=response,
            deployer_id=deployer_id,
            prompt_text=prompt,
            model_id=model,
            image_bytes_iter=image_blobs or None,
            signer=signer,
            emitter=emitter,
            open_model=open_model,
            regulatory_context=regulatory_context,
            user_session_id=user_session_id,
        )
    except Exception as exc:  # noqa: BLE001
        # C7: never break the caller's image path.
        logger.warning("LedgerProof FLUX receipt failed: %s", exc)
    return response, signed
