"""Chat session wrapper tests (mocked ChatSession, no network)."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from ledgerproof_google_ai import LedgerProofGenerativeModel, QueueEmitter
from ledgerproof_google_ai.signer import Ed25519Signer


def _fake_response(text="Hi back."):
    part = SimpleNamespace(text=text, function_call=None)
    cand = SimpleNamespace(
        content=SimpleNamespace(parts=[part], role="model"),
        finish_reason="STOP",
    )
    return SimpleNamespace(
        text=text,
        candidates=[cand],
        usage_metadata=SimpleNamespace(
            prompt_token_count=3,
            candidates_token_count=2,
            total_token_count=5,
        ),
        response_id="resp_chat_001",
        model_version="gemini-2.0-flash",
    )


def _make_chat(captured):
    fake_inner_chat = MagicMock()
    fake_inner_chat.send_message.return_value = _fake_response()
    fake_inner_chat.history = []
    fake_inner_model = MagicMock()
    fake_inner_model.start_chat.return_value = fake_inner_chat
    wrapper = LedgerProofGenerativeModel(
        fake_inner_model,
        deployer_id="acme-eu-test",
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )
    return wrapper.start_chat()


def test_chat_send_message_emits_one_receipt_per_turn():
    captured: list = []
    chat = _make_chat(captured)
    chat.send_message("Hi")
    chat.send_message("How are you?")
    assert len(captured) == 2
    for signed in captured:
        receipt = signed["receipt"]
        assert receipt["schema"] == "chatbot_session/v1"
        assert receipt["streaming"] is False
        assert receipt["deployer_id"] == "acme-eu-test"


def test_chat_history_proxies_to_inner():
    captured: list = []
    chat = _make_chat(captured)
    # The fake_inner_chat sets history = []; we just confirm passthrough works.
    assert chat.history == []


def test_chat_streaming_send_message_emits_streaming_receipt():
    captured: list = []
    chunks = [
        SimpleNamespace(text="One ", function_call=None, candidates=[]),
        SimpleNamespace(text="two ", function_call=None, candidates=[]),
        SimpleNamespace(text="three.", function_call=None, candidates=[]),
    ]

    fake_inner_chat = MagicMock()
    fake_inner_chat.send_message.return_value = iter(chunks)

    fake_inner_model = MagicMock()
    fake_inner_model.start_chat.return_value = fake_inner_chat

    wrapper = LedgerProofGenerativeModel(
        fake_inner_model,
        deployer_id="acme-eu-test",
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )
    chat = wrapper.start_chat()
    stream = chat.send_message("Count to three.", stream=True)
    text = "".join(c.text for c in stream)
    assert text == "One two three."

    assert len(captured) == 1
    receipt = captured[0]["receipt"]
    assert receipt["streaming"] is True
    asst = next(c for c in receipt["content_refs"] if c["role"] == "model")
    assert asst["byte_length"] == len("One two three.".encode("utf-8"))
