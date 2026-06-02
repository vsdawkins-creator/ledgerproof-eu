"""Manual emit_receipt and decorator tests."""

from __future__ import annotations

import base64
from types import SimpleNamespace

import pytest

from ledgerproof_ai21 import (
    QueueEmitter,
    emit_receipt,
    extract_tool_uses,
    lpr_track,
)
from ledgerproof_ai21.canonical import canonical_encode
from ledgerproof_ai21.signer import Ed25519Signer, verify


def _fake_response(text: str = "Long-context Jamba reply."):
    message = SimpleNamespace(role="assistant", content=text, tool_calls=None)
    choice = SimpleNamespace(index=0, message=message, finish_reason="stop")
    return SimpleNamespace(
        id="cmpl_manual_001",
        model="jamba-1.5-mini",
        choices=[choice],
        usage=SimpleNamespace(prompt_tokens=4, completion_tokens=8, total_tokens=12),
    )


def test_manual_emit_receipt_signs_and_emits():
    captured: list = []
    signer = Ed25519Signer()
    signed = emit_receipt(
        response=_fake_response(),
        deployer_id="acme-eu-test",
        user_message_text="hello jamba",
        signer=signer,
        emitter=QueueEmitter(captured.append),
    )
    assert len(captured) == 1
    assert signed["signature_alg"] == "ed25519"
    # C4: verifiable offline.
    canonical_bytes = canonical_encode(signed["receipt"])
    sig = base64.b64decode(signed["signature_b64"])
    assert verify(signer.public_key_bytes(), canonical_bytes, sig)


def test_manual_emit_receipt_with_long_context_dict():
    captured: list = []
    emit_receipt(
        response=_fake_response(),
        deployer_id="acme-eu-test",
        emitter=QueueEmitter(captured.append),
        schema="long_context_inference/v1",
        long_context={
            "declared_context_window": 262144,
            "effective_input_tokens": 200_000,
        },
    )
    payload = captured[0]["receipt"]
    assert payload["schema"] == "long_context_inference/v1"
    assert payload["long_context"]["declared_context_window"] == 262144


def test_decorator_emits_receipt_around_sync_call():
    captured: list = []

    @lpr_track(
        deployer_id="acme-eu-test",
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
        user_message_kwarg="user_text",
    )
    def my_function(user_text: str):
        return _fake_response(text="decorated reply")

    out = my_function(user_text="hello there")
    assert out.choices[0].message.content == "decorated reply"
    assert len(captured) == 1
    assert captured[0]["receipt"]["deployer_id"] == "acme-eu-test"


def test_extract_tool_uses_handles_openai_compatible_shape():
    tool_call = SimpleNamespace(
        id="call_xyz",
        function=SimpleNamespace(name="lookup", arguments='{"q": "jamba"}'),
    )
    message = SimpleNamespace(role="assistant", content=None, tool_calls=[tool_call])
    choice = SimpleNamespace(index=0, message=message, finish_reason="tool_calls")
    response = SimpleNamespace(id="x", model="jamba-1.5-large", choices=[choice], usage=None)

    refs = extract_tool_uses(response)
    assert len(refs) == 1
    assert refs[0].tool_name == "lookup"
    assert refs[0].tool_use_id == "call_xyz"
    assert len(refs[0].input_sha256_hex) == 64


def test_decorator_swallows_emitter_failure():
    """Decorator emission failure must NOT break the wrapped function (C7)."""

    class _Boom:
        def emit(self, _):
            raise RuntimeError("nope")

    @lpr_track(
        deployer_id="acme-eu-test",
        emitter=_Boom(),
        signer=Ed25519Signer(),
    )
    def my_function():
        return _fake_response()

    out = my_function()
    assert out.id == "cmpl_manual_001"
