"""Decorator-based emission tests."""

from __future__ import annotations

import base64

from ledgerproof_replicate import QueueEmitter, lpr_track
from ledgerproof_replicate.canonical import canonical_encode
from ledgerproof_replicate.signer import Ed25519Signer, verify


def test_sync_decorator_emits_receipt():
    captured: list = []
    signer = Ed25519Signer()

    @lpr_track(
        deployer_id="acme-eu",
        signer=signer,
        emitter=QueueEmitter(captured.append),
    )
    def my_call(ref: str, input: dict):
        return "generated answer text"

    result = my_call(
        ref="meta/meta-llama-3-70b-instruct",
        input={"prompt": "Explain Article 50"},
    )
    assert result == "generated answer text"

    assert len(captured) == 1
    signed = captured[0]
    assert signed["receipt"]["deployer_id"] == "acme-eu"
    assert signed["receipt"]["model"]["model_id"] == "meta/meta-llama-3-70b-instruct"
    assert signed["receipt"]["schema"] in ("chatbot_session/v1", "generated_content/v1")

    # Verify signature
    canonical = canonical_encode(signed["receipt"])
    sig = base64.b64decode(signed["signature_b64"])
    assert verify(signer.public_key_bytes(), canonical, sig)


def test_async_decorator_emits_receipt():
    import asyncio

    captured: list = []

    @lpr_track(
        deployer_id="acme-eu",
        emitter=QueueEmitter(captured.append),
    )
    async def my_async_call(ref: str, input: dict):
        return "hello"

    result = asyncio.run(
        my_async_call(
            ref="meta/meta-llama-3-70b-instruct",
            input={"prompt": "hi"},
        )
    )
    assert result == "hello"
    assert len(captured) == 1
    assert captured[0]["receipt"]["deployer_id"] == "acme-eu"


def test_decorator_accepts_tuple_return_for_full_control():
    captured: list = []

    @lpr_track(deployer_id="acme-eu", emitter=QueueEmitter(captured.append))
    def my_call():
        # (ref, output, inputs)
        return (
            "black-forest-labs/flux-schnell:bf2f2e683d03a9549f484a37a0df1c4c08e8e3fa3a18f3e1c1d4a4dba8c0bc0e",
            ["https://replicate.delivery/pbxt/abc/out.png"],
            {"prompt": "a lake"},
        )

    my_call()
    signed = captured[0]
    assert signed["receipt"]["schema"] == "synthetic_image/v1"
    assert signed["receipt"]["model"]["model_version"].startswith("bf2f2e")


def test_decorator_skips_when_ref_missing():
    captured: list = []

    @lpr_track(deployer_id="acme-eu", emitter=QueueEmitter(captured.append))
    def my_call():
        return "x"

    my_call()  # no ref kwarg, no tuple return
    assert captured == []
