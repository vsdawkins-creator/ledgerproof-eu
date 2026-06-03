"""Tests for manual emission and the @lpr_track decorator."""

from __future__ import annotations

from types import SimpleNamespace

from ledgerproof_reka import (
    QueueEmitter,
    emit_receipt,
    extract_tool_uses,
    lpr_track,
)
from ledgerproof_reka.signer import Ed25519Signer


def _fake_response(text="Synthesised paragraph.", with_tool_use=False):
    tool_calls = []
    if with_tool_use:
        tool_calls.append(
            SimpleNamespace(name="web_search", id="tu_a", arguments={"q": "EU AI Act"})
        )
    message = SimpleNamespace(content=text, tool_calls=tool_calls or None)
    first = SimpleNamespace(
        message=message,
        finish_reason="stop",
        tool_calls=tool_calls or None,
    )
    return SimpleNamespace(
        id="resp_manual_001",
        model="reka-core",
        responses=[first],
        usage=SimpleNamespace(input_tokens=12, output_tokens=24),
    )


def test_manual_emit_generated_content_schema_carries_through():
    captured: list = []
    signed = emit_receipt(
        response=_fake_response(),
        deployer_id="acme-eu",
        schema="generated_content/v1",
        signer=Ed25519Signer(),
        emitter=QueueEmitter(captured.append),
        user_message_text="Write me a paragraph.",
    )
    assert signed["receipt"]["schema"] == "generated_content/v1"
    assert signed["receipt"]["model"]["provider"] == "reka"
    assert captured and captured[0] == signed


def test_manual_emit_includes_user_and_assistant_content_refs():
    captured: list = []
    emit_receipt(
        response=_fake_response(text="abcdef"),
        deployer_id="acme-eu",
        signer=Ed25519Signer(),
        emitter=QueueEmitter(captured.append),
        user_message_text="hello",
    )
    roles = [c["role"] for c in captured[0]["receipt"]["content_refs"]]
    assert "user" in roles and "assistant" in roles


def test_extract_tool_uses_handles_dict_shape():
    """Defensive: some SDK versions return plain dicts for tool_calls."""
    resp = SimpleNamespace(
        id="r",
        model="reka-flash-3.1",
        responses=[
            SimpleNamespace(
                message=SimpleNamespace(content="ok"),
                tool_calls=[
                    {"name": "calc", "id": "tu_z", "arguments": {"x": 1}},
                ],
            )
        ],
    )
    refs = extract_tool_uses(resp)
    assert len(refs) == 1
    assert refs[0].tool_name == "calc"
    assert refs[0].tool_use_id == "tu_z"


def test_lpr_track_decorator_emits_on_sync_function():
    captured: list = []
    signer = Ed25519Signer()

    @lpr_track(
        deployer_id="acme-eu",
        signer=signer,
        emitter=QueueEmitter(captured.append),
        user_message_kwarg="prompt",
    )
    def call_reka(*, prompt: str):
        return _fake_response(text=f"echo:{prompt}")

    result = call_reka(prompt="Hi from decorator")
    assert result.id == "resp_manual_001"
    assert len(captured) == 1
    assert captured[0]["receipt"]["deployer_id"] == "acme-eu"


def test_lpr_track_decorator_swallows_emission_errors():
    """Failure to emit must not break the wrapped function."""

    class BoomEmitter:
        def emit(self, _):
            raise RuntimeError("nope")

    @lpr_track(
        deployer_id="acme-eu",
        signer=Ed25519Signer(),
        emitter=BoomEmitter(),
    )
    def call_reka():
        return _fake_response()

    result = call_reka()
    assert result.id == "resp_manual_001"
