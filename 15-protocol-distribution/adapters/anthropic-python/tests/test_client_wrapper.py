"""
Client wrapper tests using mocked Anthropic clients (no network).

We mock the inner `anthropic.Anthropic` / `AsyncAnthropic` instances so the tests
run on a fresh venv without an API key.
"""

from __future__ import annotations

import asyncio
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from ledgerproof_anthropic import (
    LedgerProofAnthropic,
    LedgerProofAsyncAnthropic,
    QueueEmitter,
)
from ledgerproof_anthropic.signer import Ed25519Signer, verify
from ledgerproof_anthropic.canonical import canonical_encode
import base64


def _fake_message(text="Hello, world.", with_tool_use=False, response_id="msg_test_001"):
    text_block = SimpleNamespace(type="text", text=text)
    blocks = [text_block]
    if with_tool_use:
        blocks.append(
            SimpleNamespace(
                type="tool_use",
                name="bash",
                id="toolu_test_1",
                input={"cmd": "ls"},
            )
        )
    return SimpleNamespace(
        id=response_id,
        model="claude-opus-4-1",
        content=blocks,
        stop_reason="end_turn",
        usage=SimpleNamespace(input_tokens=10, output_tokens=20),
    )


def _make_wrapper(emitter_sink, with_tool_use=False):
    fake_inner = MagicMock()
    fake_inner.messages.create.return_value = _fake_message(with_tool_use=with_tool_use)
    return LedgerProofAnthropic(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(emitter_sink.append),
        signer=Ed25519Signer(),
    )


def test_sync_create_emits_receipt_and_returns_response_unchanged():
    captured: list = []
    wrapper = _make_wrapper(captured)
    response = wrapper.messages.create(
        model="claude-opus-4-1",
        max_tokens=64,
        messages=[{"role": "user", "content": "Hi there"}],
    )
    # C7: response is passed through unchanged.
    assert response.id == "msg_test_001"
    assert response.content[0].text == "Hello, world."

    assert len(captured) == 1
    signed = captured[0]
    assert signed["signature_alg"] == "ed25519"
    assert signed["receipt"]["deployer_id"] == "acme-eu-test"
    assert signed["receipt"]["schema"] == "chatbot_session/v1"
    assert signed["receipt"]["streaming"] is False
    # Two content refs: user + assistant
    roles = [c["role"] for c in signed["receipt"]["content_refs"]]
    assert "user" in roles and "assistant" in roles


def test_sync_create_with_tool_use_promotes_to_agent_action_schema():
    captured: list = []
    wrapper = _make_wrapper(captured, with_tool_use=True)
    wrapper.messages.create(
        model="claude-opus-4-1",
        max_tokens=64,
        messages=[{"role": "user", "content": "Run ls"}],
    )
    signed = captured[0]
    assert signed["receipt"]["schema"] == "agent_action/v1"
    assert signed["receipt"]["tool_uses"][0]["tool_name"] == "bash"
    assert signed["receipt"]["tool_uses"][0]["tool_use_id"] == "toolu_test_1"


def test_sync_streaming_emits_receipt_with_incremental_hash():
    captured: list = []

    @contextmanager
    def fake_stream(**kwargs):
        class _S:
            def __init__(self):
                self.text_stream = iter(["Hel", "lo, ", "world."])

            def get_final_message(self):
                return _fake_message(text="Hello, world.")

        yield _S()

    fake_inner = MagicMock()
    fake_inner.messages.stream = fake_stream

    wrapper = LedgerProofAnthropic(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )
    with wrapper.messages.stream(
        model="claude-opus-4-1",
        max_tokens=64,
        messages=[{"role": "user", "content": "Hi"}],
    ) as stream:
        text = "".join(stream.text_stream)
    assert text == "Hello, world."

    assert len(captured) == 1
    signed = captured[0]
    assert signed["receipt"]["streaming"] is True
    # Assistant content_ref byte_length must equal the streamed bytes.
    asst = next(c for c in signed["receipt"]["content_refs"] if c["role"] == "assistant")
    assert asst["byte_length"] == len("Hello, world.".encode("utf-8"))


def test_async_create_emits_receipt():
    captured: list = []

    fake_inner = MagicMock()
    fake_inner.messages.create = AsyncMock(return_value=_fake_message())

    wrapper = LedgerProofAsyncAnthropic(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )

    async def _run():
        response = await wrapper.messages.create(
            model="claude-opus-4-1",
            max_tokens=64,
            messages=[{"role": "user", "content": "Hi async"}],
        )
        assert response.id == "msg_test_001"

    asyncio.run(_run())

    assert len(captured) == 1
    assert captured[0]["receipt"]["deployer_id"] == "acme-eu-test"


def test_signature_verifies_with_published_public_key():
    """C4: offline verification works given the public key bytes."""
    captured: list = []
    signer = Ed25519Signer()
    fake_inner = MagicMock()
    fake_inner.messages.create.return_value = _fake_message()
    wrapper = LedgerProofAnthropic(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=signer,
    )
    wrapper.messages.create(
        model="claude-opus-4-1",
        max_tokens=64,
        messages=[{"role": "user", "content": "Verify me"}],
    )
    signed = captured[0]
    canonical_bytes = canonical_encode(signed["receipt"])
    sig = base64.b64decode(signed["signature_b64"])
    assert verify(signer.public_key_bytes(), canonical_bytes, sig)
