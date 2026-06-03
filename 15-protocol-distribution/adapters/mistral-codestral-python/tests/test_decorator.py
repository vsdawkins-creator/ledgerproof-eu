"""Decorator tests."""

from __future__ import annotations

from types import SimpleNamespace

from ledgerproof_mistral_codestral import (
    QueueEmitter,
    lpr_track,
)
from ledgerproof_mistral_codestral.signer import Ed25519Signer


def _fake_response(text="def hello(): pass\n"):
    message = SimpleNamespace(role="assistant", content=text, tool_calls=None)
    choice = SimpleNamespace(index=0, message=message, finish_reason="stop")
    return SimpleNamespace(
        id="cmpl_dec_001",
        model="codestral-latest",
        choices=[choice],
        usage=SimpleNamespace(prompt_tokens=5, completion_tokens=4, total_tokens=9),
    )


def test_lpr_track_emits_receipt_for_sync_function():
    captured: list = []
    signer = Ed25519Signer()

    @lpr_track(
        deployer_id="acme-eu",
        emitter=QueueEmitter(captured.append),
        signer=signer,
        user_message_kwarg="user_prompt",
    )
    def my_fn(*, user_prompt: str):
        return _fake_response(text=f"# generated for: {user_prompt}\npass\n")

    out = my_fn(user_prompt="Write a hello function")
    assert out.id == "cmpl_dec_001"
    assert len(captured) == 1
    signed = captured[0]
    assert signed["receipt"]["deployer_id"] == "acme-eu"
    assert signed["receipt"]["schema"] == "generated_code/v1"
    # user content_ref should be present since we declared user_message_kwarg
    roles = [c["role"] for c in signed["receipt"]["content_refs"]]
    assert "user" in roles and "assistant" in roles


def test_lpr_track_handles_emitter_failure_gracefully():
    class _Boom:
        def emit(self, _):
            raise RuntimeError("nope")

    @lpr_track(deployer_id="acme-eu", emitter=_Boom())
    def my_fn():
        return _fake_response()

    # Must not raise.
    out = my_fn()
    assert out.id == "cmpl_dec_001"
