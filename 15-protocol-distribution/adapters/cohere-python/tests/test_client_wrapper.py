"""
Client wrapper tests using mocked Cohere clients (no network).

We mock the inner `cohere.ClientV2` / `AsyncClientV2` instances so the tests
run on a fresh venv without a Cohere API key.
"""

from __future__ import annotations

import asyncio
import base64
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from ledgerproof_cohere import (
    LedgerProofAsyncCohere,
    LedgerProofCohere,
    QueueEmitter,
)
from ledgerproof_cohere.canonical import canonical_encode
from ledgerproof_cohere.signer import Ed25519Signer, verify


def _fake_chat_response(text="Hello, world.", with_tool_use=False, response_id="resp_test_001"):
    """Mock a Cohere V2 ChatResponse."""
    text_block = SimpleNamespace(type="text", text=text)
    message = SimpleNamespace(
        role="assistant",
        content=[text_block],
        tool_calls=None,
    )
    if with_tool_use:
        message.tool_calls = [
            SimpleNamespace(
                id="tc_test_1",
                type="function",
                function=SimpleNamespace(name="search_db", arguments='{"q": "ai act"}'),
            )
        ]
    return SimpleNamespace(
        id=response_id,
        model="command-a-03-2025",
        message=message,
        finish_reason="COMPLETE",
        usage=SimpleNamespace(
            tokens=SimpleNamespace(input_tokens=10, output_tokens=20),
        ),
    )


def _make_wrapper(emitter_sink, with_tool_use=False):
    fake_inner = MagicMock()
    fake_inner.chat.return_value = _fake_chat_response(with_tool_use=with_tool_use)
    return LedgerProofCohere(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(emitter_sink.append),
        signer=Ed25519Signer(),
    )


def test_sync_chat_emits_receipt_and_returns_response_unchanged():
    captured: list = []
    wrapper = _make_wrapper(captured)
    response = wrapper.chat(
        model="command-a-03-2025",
        messages=[{"role": "user", "content": "Hi there"}],
    )
    # C7: response is passed through unchanged.
    assert response.id == "resp_test_001"
    assert response.message.content[0].text == "Hello, world."

    assert len(captured) == 1
    signed = captured[0]
    assert signed["signature_alg"] == "ed25519"
    assert signed["receipt"]["deployer_id"] == "acme-eu-test"
    assert signed["receipt"]["schema"] == "chatbot_session/v1"
    assert signed["receipt"]["streaming"] is False
    assert signed["receipt"]["model"]["provider"] == "cohere"
    assert signed["receipt"]["model"]["model_id"] == "command-a-03-2025"
    assert signed["receipt"]["model"]["input_tokens"] == 10
    assert signed["receipt"]["model"]["output_tokens"] == 20
    roles = [c["role"] for c in signed["receipt"]["content_refs"]]
    assert "user" in roles and "assistant" in roles


def test_sync_chat_with_tool_use_captures_tool_calls():
    captured: list = []
    wrapper = _make_wrapper(captured, with_tool_use=True)
    wrapper.chat(
        model="command-a-03-2025",
        messages=[{"role": "user", "content": "Search the EU AI Act"}],
    )
    signed = captured[0]
    assert signed["receipt"]["tool_uses"][0]["tool_name"] == "search_db"
    assert signed["receipt"]["tool_uses"][0]["tool_call_id"] == "tc_test_1"


def test_sync_streaming_emits_receipt_with_incremental_hash():
    captured: list = []

    def fake_chat_stream(**kwargs):
        # Cohere V2 content-delta event shape.
        for delta in ["Hel", "lo, ", "world."]:
            yield SimpleNamespace(
                type="content-delta",
                delta=SimpleNamespace(
                    message=SimpleNamespace(
                        content=SimpleNamespace(text=delta),
                    ),
                ),
            )
        # message-end carries the final response.
        yield SimpleNamespace(
            type="message-end",
            response=_fake_chat_response(text="Hello, world."),
            finish_reason="COMPLETE",
        )

    fake_inner = MagicMock()
    fake_inner.chat_stream = fake_chat_stream

    wrapper = LedgerProofCohere(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )
    collected_text = []
    for event in wrapper.chat_stream(
        model="command-a-03-2025",
        messages=[{"role": "user", "content": "Hi"}],
    ):
        if getattr(event, "type", None) == "content-delta":
            collected_text.append(event.delta.message.content.text)
    assert "".join(collected_text) == "Hello, world."

    assert len(captured) == 1
    signed = captured[0]
    assert signed["receipt"]["streaming"] is True
    asst = next(c for c in signed["receipt"]["content_refs"] if c["role"] == "assistant")
    assert asst["byte_length"] == len("Hello, world.".encode("utf-8"))


def test_async_chat_emits_receipt():
    captured: list = []

    fake_inner = MagicMock()
    fake_inner.chat = AsyncMock(return_value=_fake_chat_response())

    wrapper = LedgerProofAsyncCohere(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )

    async def _run():
        response = await wrapper.chat(
            model="command-a-03-2025",
            messages=[{"role": "user", "content": "Hi async"}],
        )
        assert response.id == "resp_test_001"

    asyncio.run(_run())

    assert len(captured) == 1
    assert captured[0]["receipt"]["deployer_id"] == "acme-eu-test"


def test_signature_verifies_with_published_public_key():
    """C4: offline verification works given the public key bytes."""
    captured: list = []
    signer = Ed25519Signer()
    fake_inner = MagicMock()
    fake_inner.chat.return_value = _fake_chat_response()
    wrapper = LedgerProofCohere(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=signer,
    )
    wrapper.chat(
        model="command-a-03-2025",
        messages=[{"role": "user", "content": "Verify me"}],
    )
    signed = captured[0]
    canonical_bytes = canonical_encode(signed["receipt"])
    sig = base64.b64decode(signed["signature_b64"])
    assert verify(signer.public_key_bytes(), canonical_bytes, sig)


def test_chat_with_retrieved_documents_emits_rag_response():
    captured: list = []
    fake_inner = MagicMock()
    fake_inner.chat.return_value = _fake_chat_response(text="Per Annex IV...")
    wrapper = LedgerProofCohere(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )

    docs = [
        {"id": "doc-annex-iv", "text": "Annex IV technical documentation requirements...",
         "source_uri": "https://eur-lex.example/annex-iv"},
        {"id": "doc-art-50", "text": "Article 50 transparency obligations..."},
    ]
    rerank_results = [
        SimpleNamespace(index=1, relevance_score=0.94),
        SimpleNamespace(index=0, relevance_score=0.71),
    ]

    response = wrapper.chat_with_retrieved_documents(
        documents=docs,
        rerank_results=rerank_results,
        model="command-a-03-2025",
        messages=[{"role": "user", "content": "Summarize the AI Act"}],
    )
    assert response.id == "resp_test_001"

    signed = captured[0]
    assert signed["receipt"]["schema"] == "rag_response/v1"
    assert len(signed["receipt"]["retrieved_documents"]) == 2
    rd0 = signed["receipt"]["retrieved_documents"][0]
    rd1 = signed["receipt"]["retrieved_documents"][1]
    assert rd0["document_id"] == "doc-annex-iv"
    assert rd0["rerank_relevance_score"] == 0.71
    assert rd1["rerank_relevance_score"] == 0.94


def test_chat_with_disclosure_emits_multilingual_disclosure():
    captured: list = []
    fake_inner = MagicMock()
    fake_inner.chat.return_value = _fake_chat_response(text="Bonjour!")
    wrapper = LedgerProofCohere(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )

    response = wrapper.chat_with_disclosure(
        disclosure_text="Vous discutez avec une IA.",
        disclosure_language="fr-FR",
        disclosure_channel="chat-ui",
        model="command-a-03-2025",
        messages=[{"role": "user", "content": "Bonjour"}],
    )
    assert response.id == "resp_test_001"

    signed = captured[0]
    assert signed["receipt"]["schema"] == "multilingual_disclosure/v1"
    assert signed["receipt"]["disclosure"]["language_tag"] == "fr-FR"
    assert signed["receipt"]["disclosure"]["disclosure_channel"] == "chat-ui"


def test_response_is_not_mutated_by_adapter():
    """C7: ensure the response object is byte-identical after emission."""
    captured: list = []
    wrapper = _make_wrapper(captured)
    pre_response = _fake_chat_response()
    fake_inner = MagicMock()
    fake_inner.chat.return_value = pre_response

    wrapper2 = LedgerProofCohere(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )
    post = wrapper2.chat(
        model="command-a-03-2025",
        messages=[{"role": "user", "content": "ping"}],
    )
    assert post is pre_response
    # No extra attributes injected.
    assert not hasattr(post, "ledgerproof_receipt")
    assert not hasattr(post, "_lpr_receipt")
