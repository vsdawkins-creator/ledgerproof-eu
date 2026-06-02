"""Wrapper tests with mocked InferenceClient (no network calls)."""

from __future__ import annotations

import hashlib
import queue
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

from ledgerproof_huggingface import (
    LedgerProofAsyncInferenceClient,
    LedgerProofInferenceClient,
    QueueEmitter,
    lpr_track,
)


# ---------------------------------------------------------------------------
# Fixture builders
# ---------------------------------------------------------------------------


def _fake_chat_completion(text: str = "bonjour", id_: str = "hf-chat-1"):
    """Build an object shaped like huggingface_hub ChatCompletionOutput."""
    message = SimpleNamespace(role="assistant", content=text)
    choice = SimpleNamespace(index=0, message=message, finish_reason="stop")
    return SimpleNamespace(
        id=id_,
        model="meta-llama/Llama-3.1-70B-Instruct",
        choices=[choice],
    )


def _fake_chat_stream_chunks(parts: list[str], id_: str = "hf-stream-1"):
    for i, part in enumerate(parts):
        delta = SimpleNamespace(role="assistant" if i == 0 else None, content=part)
        choice = SimpleNamespace(index=0, delta=delta, finish_reason=None)
        yield SimpleNamespace(
            id=id_,
            model="meta-llama/Llama-3.1-70B-Instruct",
            choices=[choice],
        )


# ---------------------------------------------------------------------------
# Sync chat_completion — non-streaming
# ---------------------------------------------------------------------------


def test_sync_chat_completion_emits_receipt_and_returns_response_unmodified():
    fake = MagicMock()
    completion = _fake_chat_completion(text="bonjour")
    fake.chat_completion.return_value = completion
    fake.model = "meta-llama/Llama-3.1-70B-Instruct"

    q: queue.Queue = queue.Queue()
    client = LedgerProofInferenceClient(
        deployer_id="urn:eu:deployer:acme",
        emitter=QueueEmitter(q),
        inference_client=fake,
    )

    resp = client.chat_completion(
        messages=[{"role": "user", "content": "hi"}],
    )

    # C7 — response must be returned exactly as-is
    assert resp is completion
    assert resp.choices[0].message.content == "bonjour"

    envelope = q.get_nowait()
    assert envelope["adapter"]["name"] == "ledgerproof-huggingface"
    assert envelope["signature_alg"] == "ed25519"
    assert envelope["receipt"]["schema_id"] == "chatbot_session/v1"
    assert envelope["receipt"]["model_id"] == "meta-llama/Llama-3.1-70B-Instruct"
    assert envelope["receipt"]["deployer_id"] == "urn:eu:deployer:acme"
    assert envelope["receipt"]["model_provider"] == "huggingface"

    # response_sha256 should hash the actual text
    expected = hashlib.sha256(b"bonjour").hexdigest()
    assert envelope["receipt"]["response_sha256"] == expected


def test_sync_chat_completion_with_eu_open_model_hosted_schema():
    fake = MagicMock()
    fake.chat_completion.return_value = _fake_chat_completion()
    fake.model = "meta-llama/Llama-3.1-70B-Instruct"

    q: queue.Queue = queue.Queue()
    client = LedgerProofInferenceClient(
        deployer_id="urn:eu:deployer:acme-bank",
        regulatory_context={
            "schema": "eu_open_model_hosted/v1",
            "model_license": "llama-3.1-community-license",
            "open_weights": True,
        },
        emitter=QueueEmitter(q),
        inference_client=fake,
    )
    client.chat_completion(messages=[{"role": "user", "content": "hi"}])

    envelope = q.get_nowait()
    assert envelope["receipt"]["schema_id"] == "eu_open_model_hosted/v1"
    assert envelope["receipt"]["hosting_provider_hq"] == "Paris/NYC"
    assert envelope["receipt"]["open_weights"] is True


# ---------------------------------------------------------------------------
# Sync chat_completion — streaming
# ---------------------------------------------------------------------------


def test_sync_chat_completion_streaming_emits_receipt_after_drain():
    fake = MagicMock()
    parts = ["Hel", "lo, ", "world!"]
    fake.chat_completion.return_value = _fake_chat_stream_chunks(parts)
    fake.model = "meta-llama/Llama-3.1-70B-Instruct"

    q: queue.Queue = queue.Queue()
    client = LedgerProofInferenceClient(
        deployer_id="urn:eu:deployer:acme",
        emitter=QueueEmitter(q),
        inference_client=fake,
    )

    stream = client.chat_completion(
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


# ---------------------------------------------------------------------------
# Sync text_generation
# ---------------------------------------------------------------------------


def test_sync_text_generation_string_return_emits_receipt():
    fake = MagicMock()
    fake.text_generation.return_value = "Once upon a time"
    fake.model = "bigscience/bloom"

    q: queue.Queue = queue.Queue()
    client = LedgerProofInferenceClient(
        deployer_id="urn:eu:deployer:acme",
        emitter=QueueEmitter(q),
        inference_client=fake,
    )

    resp = client.text_generation("Tell me a story")
    assert resp == "Once upon a time"

    envelope = q.get_nowait()
    expected = hashlib.sha256(b"Once upon a time").hexdigest()
    assert envelope["receipt"]["response_sha256"] == expected
    prompt_expected = hashlib.sha256(b"Tell me a story").hexdigest()
    assert envelope["receipt"]["prompt_sha256"] == prompt_expected


# ---------------------------------------------------------------------------
# Async chat_completion
# ---------------------------------------------------------------------------


async def test_async_chat_completion_emits_receipt():
    fake_inner = MagicMock()
    completion = _fake_chat_completion(text="ciao")

    async def fake_create(*args, **kwargs):
        return completion

    fake_inner.chat_completion = fake_create
    fake_inner.model = "meta-llama/Llama-3.1-70B-Instruct"

    q: queue.Queue = queue.Queue()
    client = LedgerProofAsyncInferenceClient(
        deployer_id="urn:eu:deployer:acme",
        emitter=QueueEmitter(q),
        inference_client=fake_inner,
    )

    resp = await client.chat_completion(
        messages=[{"role": "user", "content": "hi"}]
    )

    assert resp is completion
    envelope = q.get_nowait()
    assert envelope["receipt"]["interaction_id"] == "hf-chat-1"


async def test_async_chat_completion_streaming_emits_receipt_after_drain():
    fake_inner = MagicMock()
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
        return _AsyncIter(list(_fake_chat_stream_chunks(parts)))

    fake_inner.chat_completion = fake_create
    fake_inner.model = "meta-llama/Llama-3.1-70B-Instruct"

    q: queue.Queue = queue.Queue()
    client = LedgerProofAsyncInferenceClient(
        deployer_id="urn:eu:deployer:acme",
        emitter=QueueEmitter(q),
        inference_client=fake_inner,
    )

    stream = await client.chat_completion(
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
    assert envelope["receipt"]["model_id"] == "meta-llama/Llama-3.1-70B-Instruct"


def test_decorator_does_not_break_caller_when_emitter_fails():
    class _BoomEmitter:
        def emit(self, envelope):
            raise RuntimeError("boom")

    @lpr_track(deployer_id="urn:eu:deployer:acme", emitter=_BoomEmitter())
    def ask(*, messages):
        return _fake_chat_completion()

    # Must not raise — C7 discipline
    resp = ask(messages=[{"role": "user", "content": "hi"}])
    assert resp.choices[0].message.content == "bonjour"
