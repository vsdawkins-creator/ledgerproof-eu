"""Wrapper tests with mocked AzureOpenAI clients (no network calls)."""

from __future__ import annotations

import hashlib
import queue
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pytest

from ledgerproof_azure_openai import (
    LedgerProofAsyncAzureOpenAI,
    LedgerProofAzureOpenAI,
    QueueEmitter,
    lpr_track,
)


_TENANT_HASH = hashlib.sha256(b"tenant-guid").hexdigest()
_SUB_HASH = hashlib.sha256(b"subscription-guid").hexdigest()
_PRINCIPAL_HASH = hashlib.sha256(b"principal-oid").hexdigest()


def _fake_chat_completion(text: str = "hello world", id_: str = "chatcmpl-abc"):
    """Build an object shaped like openai.types.chat.ChatCompletion."""
    message = SimpleNamespace(role="assistant", content=text)
    choice = SimpleNamespace(index=0, message=message, finish_reason="stop")
    return SimpleNamespace(
        id=id_,
        model="gpt-4o-2024-08-06",
        choices=[choice],
        usage=SimpleNamespace(prompt_tokens=3, completion_tokens=2, total_tokens=5),
    )


def _fake_stream_chunks(parts: list[str], id_: str = "chatcmpl-stream"):
    for i, part in enumerate(parts):
        delta = SimpleNamespace(role="assistant" if i == 0 else None, content=part)
        choice = SimpleNamespace(index=0, delta=delta, finish_reason=None)
        yield SimpleNamespace(id=id_, model="gpt-4o-2024-08-06", choices=[choice])


def _build_mock_azure_client() -> Any:
    """Build a MagicMock that exposes .chat.completions.create()."""
    inner = MagicMock()
    inner.chat = MagicMock()
    inner.chat.completions = MagicMock()
    return inner


# ---------------------------------------------------------------------------
# Sync, non-streaming, baseline schema
# ---------------------------------------------------------------------------


def test_sync_non_streaming_emits_receipt_and_returns_response_unmodified():
    fake = _build_mock_azure_client()
    completion = _fake_chat_completion(text="bonjour")
    fake.chat.completions.create.return_value = completion

    q: queue.Queue = queue.Queue()
    client = LedgerProofAzureOpenAI(
        deployer_id="urn:eu:deployer:contoso-bank",
        emitter=QueueEmitter(q),
        azure_client=fake,
    )

    resp = client.chat.completions.create(
        model="gpt4-prod",
        messages=[{"role": "user", "content": "hi"}],
    )

    # C7 — response must be returned exactly as-is
    assert resp is completion
    assert resp.choices[0].message.content == "bonjour"

    envelope = q.get_nowait()
    assert envelope["adapter"]["name"] == "ledgerproof-azure-openai"
    assert envelope["signature_alg"] == "ed25519"
    assert envelope["receipt"]["schema_id"] == "chatbot_session/v1"
    assert envelope["receipt"]["model_provider"] == "azure-openai"
    assert envelope["receipt"]["deployer_id"] == "urn:eu:deployer:contoso-bank"


# ---------------------------------------------------------------------------
# Azure enterprise schema captures deployment + endpoint
# ---------------------------------------------------------------------------


def test_azure_enterprise_schema_captures_deployment_and_endpoint():
    fake = _build_mock_azure_client()
    fake.chat.completions.create.return_value = _fake_chat_completion()

    q: queue.Queue = queue.Queue()
    client = LedgerProofAzureOpenAI(
        deployer_id="urn:eu:deployer:contoso-bank",
        emitter=QueueEmitter(q),
        azure_client=fake,
        regulatory_context={
            "schema": "azure_enterprise_session/v1",
            "azure_endpoint": "https://contoso-weu.openai.azure.com/",
            "api_version": "2024-08-01-preview",
            "tenant_id_hash": _TENANT_HASH,
            "subscription_id_hash": _SUB_HASH,
        },
    )

    client.chat.completions.create(
        model="gpt4-prod",
        messages=[{"role": "user", "content": "hi"}],
    )

    envelope = q.get_nowait()
    receipt = envelope["receipt"]
    assert receipt["schema_id"] == "azure_enterprise_session/v1"
    assert receipt["azure_deployment"] == "gpt4-prod"
    assert receipt["azure_endpoint"] == "https://contoso-weu.openai.azure.com/"
    assert receipt["azure_region"] == "westeurope"  # guessed from -weu suffix
    assert receipt["api_version"] == "2024-08-01-preview"
    assert receipt["tenant_id_hash"] == _TENANT_HASH


# ---------------------------------------------------------------------------
# Azure AD authenticated schema
# ---------------------------------------------------------------------------


def test_azure_ad_authenticated_schema_captures_principal_hash():
    fake = _build_mock_azure_client()
    fake.chat.completions.create.return_value = _fake_chat_completion()

    q: queue.Queue = queue.Queue()
    client = LedgerProofAzureOpenAI(
        deployer_id="urn:eu:deployer:contoso-bank",
        emitter=QueueEmitter(q),
        azure_client=fake,
        regulatory_context={
            "schema": "azure_ad_authenticated_session/v1",
            "azure_endpoint": "https://contoso-neu.openai.azure.com/",
            "api_version": "2024-08-01-preview",
            "azure_ad_principal_hash": _PRINCIPAL_HASH,
            "azure_ad_principal_type": "managed_identity",
            "auth_method": "managed_identity",
        },
    )

    client.chat.completions.create(
        model="gpt4-prod",
        messages=[{"role": "user", "content": "hi"}],
    )

    envelope = q.get_nowait()
    receipt = envelope["receipt"]
    assert receipt["schema_id"] == "azure_ad_authenticated_session/v1"
    assert receipt["azure_ad_principal_hash"] == _PRINCIPAL_HASH
    assert receipt["azure_ad_principal_type"] == "managed_identity"
    assert receipt["azure_region"] == "northeurope"


# ---------------------------------------------------------------------------
# Sync, streaming
# ---------------------------------------------------------------------------


def test_sync_streaming_emits_receipt_after_drain_with_full_text_hash():
    fake = _build_mock_azure_client()
    parts = ["Bonjour, ", "le ", "monde", "!"]
    fake.chat.completions.create.return_value = _fake_stream_chunks(parts)

    q: queue.Queue = queue.Queue()
    client = LedgerProofAzureOpenAI(
        deployer_id="urn:eu:deployer:contoso-bank",
        emitter=QueueEmitter(q),
        azure_client=fake,
    )

    stream = client.chat.completions.create(
        model="gpt4-prod",
        messages=[{"role": "user", "content": "hi"}],
        stream=True,
    )

    # Receipt must NOT have been emitted yet
    assert q.empty()

    seen = list(stream)
    assert len(seen) == 4

    envelope = q.get_nowait()
    expected = hashlib.sha256("".join(parts).encode("utf-8")).hexdigest()
    assert envelope["receipt"]["response_sha256"] == expected
    assert envelope["receipt"]["extra"]["streaming"] is True


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
    client = LedgerProofAsyncAzureOpenAI(
        deployer_id="urn:eu:deployer:contoso-bank",
        emitter=QueueEmitter(q),
        azure_client=fake_inner,
    )

    resp = await client.chat.completions.create(
        model="gpt4-prod", messages=[{"role": "user", "content": "hi"}]
    )

    assert resp is completion
    envelope = q.get_nowait()
    assert envelope["receipt"]["interaction_id"] == "chatcmpl-abc"


# ---------------------------------------------------------------------------
# Async, streaming
# ---------------------------------------------------------------------------


async def test_async_streaming_emits_receipt_after_drain():
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
    client = LedgerProofAsyncAzureOpenAI(
        deployer_id="urn:eu:deployer:contoso-bank",
        emitter=QueueEmitter(q),
        azure_client=fake_inner,
    )

    stream = await client.chat.completions.create(
        model="gpt4-prod",
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

    @lpr_track(deployer_id="urn:eu:deployer:contoso-bank", emitter=QueueEmitter(q))
    def ask(question: str, *, messages):
        return _fake_chat_completion(text=f"echo: {question}")

    resp = ask("ping", messages=[{"role": "user", "content": "ping"}])
    assert resp.choices[0].message.content == "echo: ping"

    envelope = q.get_nowait()
    assert envelope["receipt"]["model_id"] == "gpt-4o-2024-08-06"
    assert envelope["receipt"]["model_provider"] == "azure-openai"


def test_decorator_does_not_break_caller_when_emitter_fails():
    class _BoomEmitter:
        def emit(self, envelope):
            raise RuntimeError("boom")

    @lpr_track(
        deployer_id="urn:eu:deployer:contoso-bank", emitter=_BoomEmitter()
    )
    def ask(*, messages):
        return _fake_chat_completion()

    # Must not raise — C7 discipline
    resp = ask(messages=[{"role": "user", "content": "hi"}])
    assert resp.choices[0].message.content == "hello world"


def test_streaming_receipt_failure_swallowed():
    """C7: even a schema-construction failure inside the stream flush
    must not propagate to the caller."""

    class _BoomEmitter:
        def emit(self, envelope):
            raise RuntimeError("boom")

    fake = _build_mock_azure_client()
    fake.chat.completions.create.return_value = _fake_stream_chunks(["a", "b"])

    client = LedgerProofAzureOpenAI(
        deployer_id="urn:eu:deployer:contoso-bank",
        emitter=_BoomEmitter(),
        azure_client=fake,
    )

    stream = client.chat.completions.create(
        model="gpt4-prod",
        messages=[{"role": "user", "content": "hi"}],
        stream=True,
    )
    # Drain — must not raise.
    list(stream)
