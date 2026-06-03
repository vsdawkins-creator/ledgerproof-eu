"""Tests for the standalone FLUX image-wrapper helper."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from ledgerproof_fireworks import QueueEmitter
from ledgerproof_fireworks.image_wrapper import generate_flux_with_receipt
from ledgerproof_fireworks.signer import Ed25519Signer


def test_generate_flux_with_receipt_returns_response_and_signed_receipt():
    captured: list = []
    fake_response = SimpleNamespace(
        id="img_002",
        model="accounts/fireworks/models/flux-1-schnell-fp8",
        image_bytes=b"\x89PNG\r\n\x1a\nblob",
    )
    fake_client = MagicMock()
    fake_client.image.generate.return_value = fake_response

    response, signed = generate_flux_with_receipt(
        client=fake_client,
        deployer_id="acme-eu",
        model="accounts/fireworks/models/flux-1-schnell-fp8",
        prompt="alpine lake at sunrise",
        signer=Ed25519Signer(),
        emitter=QueueEmitter(captured.append),
    )

    # C7: response is the SAME object the underlying client returned.
    assert response is fake_response
    assert signed["receipt"]["schema"] == "flux_image_generation/v1"
    assert signed["receipt"]["model"]["model_id"].endswith("flux-1-schnell-fp8")
    roles = [c["role"] for c in signed["receipt"]["content_refs"]]
    assert "user" in roles and "image" in roles
    assert captured and captured[0] is signed


def test_generate_flux_with_receipt_swallows_receipt_errors():
    """Even if the receipt path blows up, the FLUX response must come through."""
    fake_response = SimpleNamespace(id="img_003", model="accounts/fireworks/models/flux-1-dev-fp8")
    fake_client = MagicMock()
    fake_client.image.generate.return_value = fake_response

    class _Boom:
        def emit(self, _):
            raise RuntimeError("nope")

    response, signed = generate_flux_with_receipt(
        client=fake_client,
        deployer_id="acme-eu",
        model="accounts/fireworks/models/flux-1-dev-fp8",
        prompt="any",
        signer=Ed25519Signer(),
        emitter=_Boom(),
    )
    assert response is fake_response
    # signed may or may not be populated depending on where the error landed;
    # the important contract is that no exception escaped.
    assert isinstance(signed, dict)
