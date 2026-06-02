"""Wrapper tests with mocked OpenAI clients (no network calls)."""

from __future__ import annotations

import queue
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pytest

from ledgerproof_xai import (
    LedgerProofAsyncXAI,
    LedgerProofXAI,
    QueueEmitter,
    lpr_track,
)


def _fake_chat_completion(
    text: str = "hello world",
    id_: str = "grok-cmpl-abc",
    model: str = "grok-2-latest",
):
    """Build an object shaped like openai.types.chat.ChatCompletion (Grok flavor)."""
    message = SimpleNamespace(role="assistant", content=text)
    choice = SimpleNamespace(index=0, message=message, finish_reason="stop")
    return SimpleNamespace(
        id=id_,
        model=model,
        choices=[choice],
        usage=SimpleNamespace(prompt_tokens=3, completion_tokens=2, total_tokens=5),
    )


def _fake_stream_chunks(parts: list[str], id_: str = "grok-stream", model: str = "grok-2-latest"):
    for i, part in enumerate(parts):
        delta = SimpleNamespace(role="assistant" if i == 0 else None, content=part)
        choice = SimpleNamespace(index=0, delta=delta, finish_reason=None)
        yield SimpleNamespace(id=id_, model=model, choices=[choice])


def _build_mock_openai() -> Any:
    inner = MagicMock()
    inner.chat = MagicMock()
    inner.chat.completions = MagicMock()
    return inner


# ---------------------------------------------------------------------------
# Sync, non-streaming
# ---------------------------------------------------------------------------


def test_sync_non_streaming_emits_receipt_and_returns_response_unmodified():
    fake = _build_mock_openai()
    completion = _fake_chat_completion(text="bonjour")
    fake.chat.completions.create.return_value = completion

    q: queue.Queue = queue.Queue()
    client = LedgerProofXAI(
        deployer_id="urn:eu:deployer:acme",
        emitter=QueueEmitter(q),
        openai_client=fake,
    )

    resp = client.chat.completions.create(
        model="grok-2-latest",
        messages=[{"role": "user", "content": "hi"}],
    )

    # C7 — response must be returned exactly as-is
    assert resp is completion
    assert resp.choices[0].message.content == "bonjour"

    envelope = q.get_nowait()
    assert envelope["adapter"]["name"] == "ledgerproof-xai"
    assert envelope["signature_alg"] == "ed25519"
    assert envelope["receipt"]["schema_id"] == "chatbot_session/v1"
    assert envelope["receipt"]["model_id"] == "grok-2-latest"
    assert envelope["receipt"]["model_provider"] == "xai"
    assert envelope["receipt"]["deployer_id"] == "urn:eu:deployer:acme"
    assert envelope["receipt"]["extra"]["provider"] == "xai"


def test_sync_realtime_data_schema_carries_attribution_fields():
    fake = _build_mock_openai()
    fake.chat.completions.create.return_value = _fake_chat_completion(
        text="As of today, X reports..."
    )

    q: queue.Queue = queue.Queue()
    import hashlib
    sources_hash = hashlib.sha256(b"[]").hexdigest()
    client = LedgerProofXAI(
        deployer_id="urn:eu:deployer:acme",
        regulatory_context={
            "schema": "realtime_data_inference/v1",
            "realtime_data_used": True,
            "realtime_sources_sha256": sources_hash,
            "public_interest_text": True,
        },
        emitter=QueueEmitter(q),
        openai_client=fake,
    )
    client.chat.completions.create(
        model="grok-2-latest",
        messages=[{"role": "user", "content": "What's trending?"}],
    )
    env = q.get_nowait()
    assert env["receipt"]["schema_id"] == "realtime_data_inference/v1"
    assert env["receipt"]["realtime_data_used"] is True
    assert env["receipt"]["realtime_sources_sha256"] == sources_hash
    assert env["receipt"]["public_interest_text"] is True


def test_sync_vision_schema_detects_image_blocks():
    fake = _build_mock_openai()
    fake.chat.completions.create.return_value = _fake_chat_completion(
        text="I see a cat.", model="grok-2-vision"
    )

    q: queue.Queue = queue.Queue()
    client = LedgerProofXAI(
        deployer_id="urn:eu:deployer:acme",
        regulatory_context={"schema": "vision_inference/v1"},
        emitter=QueueEmitter(q),
        openai_client=fake,
    )
    client.chat.completions.create(
        model="grok-2-vision",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "what is this?"},
                    {"type": "image_url", "image_url": {"url": "https://x.com/i.png"}},
                ],
            }
        ],
    )
    env = q.get_nowait()
    assert env["receipt"]["schema_id"] == "vision_inference/v1"
    assert env["receipt"]["image_count"] == 1
    assert env["receipt"]["content_modality"] == "image"


# ---------------------------------------------------------------------------
# Sync, streaming
# ---------------------------------------------------------------------------


def test_sync_streaming_emits_receipt_after_drain_with_full_text_hash():
    import hashlib

    fake = _build_mock_openai()
    parts = ["Hello, ", "world", "!"]
    fake.chat.completions.create.return_value = _fake_stream_chunks(parts)

    q: queue.Queue = queue.Queue()
    client = LedgerProofXAI(
        deployer_id="urn:eu:deployer:acme",
        emitter=QueueEmitter(q),
        openai_client=fake,
    )

    stream = client.chat.completions.create(
        model="grok-2-latest",
        messages=[{"role": "user", "content": "hi"}],
        stream=True,
    )

    # Receipt must NOT have been emitted yet
    assert q.empty()

    seen = list(stream)
    assert len(seen) == 3

    envelope = q.get_nowait()
    expected = hashlib.sha256("".join(parts).encode("utf-8")).hexdigest()
    assert envelope["receipt"]["response_sha256"] == expected
    assert envelope["receipt"]["extra"]["streaming"] is True
    assert envelope["receipt"]["extra"]["provider"] == "xai"


# ---------------------------------------------------------------------------
# Async, non-streaming
# ---------------------------------------------------------------------------


async def test_async_non_streaming_emits_receipt():
    fake_inner = MagicMock()
    fake_inner.chat = MagicMock()
    fake_inner.chat.completions = MagicMock()

    completion = _fake_chat_completion(text="ciao")

    async def fake_create(*args, **kwargs):
        return completion

    fake_inner.chat.completions.create = fake_create

    q: queue.Queue = queue.Queue()
    client = LedgerProofAsyncXAI(
        deployer_id="urn:eu:deployer:acme",
        emitter=QueueEmitter(q),
        openai_client=fake_inner,
    )

    resp = await client.chat.completions.create(
        model="grok-2-latest", messages=[{"role": "user", "content": "hi"}]
    )

    assert resp is completion
    envelope = q.get_nowait()
    assert envelope["receipt"]["interaction_id"] == "grok-cmpl-abc"
    assert envelope["receipt"]["model_provider"] == "xai"


# ---------------------------------------------------------------------------
# Async, streaming
# ---------------------------------------------------------------------------


async def test_async_streaming_emits_receipt_after_drain():
    import hashlib

    fake_inner = MagicMock()
    fake_inner.chat = MagicMock()
    fake_inner.chat.completions = MagicMock()

    parts = ["abc", "def", "ghi"]

    class _AsyncIter:
        def __init__(self, items):
            self._iter = iter(items)

        def __aiter__(self):
            return self

        async def __anext__(self):
            try:
                return next(self._iter)
            except StopIteration:
                raise StopAsyncIteration

    async def fake_create(*args, **kwargs):
        return _AsyncIter(list(_fake_stream_chunks(parts)))

    fake_inner.chat.completions.create = fake_create

    q: queue.Queue = queue.Queue()
    client = LedgerProofAsyncXAI(
        deployer_id="urn:eu:deployer:acme",
        emitter=QueueEmitter(q),
        openai_client=fake_inner,
    )

    stream = await client.chat.completions.create(
        model="grok-2-latest",
        messages=[{"role": "user", "content": "hi"}],
        stream=True,
    )

    assert q.empty()

    collected = []
    async for chunk in stream:
        collected.append(chunk)
    assert len(collected) == 3

    envelope = q.get_nowait()
    expected = hashlib.sha256("".join(parts).encode("utf-8")).hexdigest()
    assert envelope["receipt"]["response_sha256"] == expected


# ---------------------------------------------------------------------------
# Decorator
# ---------------------------------------------------------------------------


def test_decorator_emits_receipt_on_sync_function():
    q: queue.Queue = queue.Queue()

    @lpr_track(deployer_id="urn:eu:deployer:acme", emitter=QueueEmitter(q))
    def ask(question: str, *, messages):
        return _fake_chat_completion(text=f"echo: {question}")

    resp = ask("ping", messages=[{"role": "user", "content": "ping"}])
    assert resp.choices[0].message.content == "echo: ping"

    envelope = q.get_nowait()
    assert envelope["receipt"]["model_id"] == "grok-2-latest"
    assert envelope["adapter"]["name"] == "ledgerproof-xai"


def test_decorator_does_not_break_caller_when_emitter_fails():
    class _BoomEmitter:
        def emit(self, envelope):
            raise RuntimeError("boom")

    @lpr_track(deployer_id="urn:eu:deployer:acme", emitter=_BoomEmitter())
    def ask(*, messages):
        return _fake_chat_completion()

    # Must not raise — C7 discipline
    resp = ask(messages=[{"role": "user", "content": "hi"}])
    assert resp.choices[0].message.content == "hello world"
