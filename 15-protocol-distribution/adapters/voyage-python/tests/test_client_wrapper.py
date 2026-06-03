"""
Client wrapper tests using mocked Voyage clients (no network).

We mock the inner `voyageai.Client` / `voyageai.AsyncClient` instances so the
tests run on a fresh venv without a Voyage API key.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from ledgerproof_voyage import (
    LedgerProofAsyncVoyage,
    LedgerProofVoyage,
    QueueEmitter,
)
from ledgerproof_voyage.canonical import canonical_encode, canonicalize_vector
from ledgerproof_voyage.signer import Ed25519Signer, verify


def _fake_embed_result():
    return SimpleNamespace(
        embeddings=[[0.11, 0.22, 0.33, 0.44]],
        total_tokens=8,
    )


def _fake_rerank_result():
    return SimpleNamespace(
        results=[
            SimpleNamespace(index=1, document="annex iv", relevance_score=0.94),
            SimpleNamespace(index=0, document="article 50", relevance_score=0.61),
        ],
        total_tokens=15,
    )


def test_sync_embed_emits_receipt_and_returns_result_unchanged():
    captured: list = []
    fake_inner = MagicMock()
    fake_inner.embed.return_value = _fake_embed_result()
    wrapper = LedgerProofVoyage(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )

    result = wrapper.embed(
        texts=["EU AI Act Article 50 text"],
        model="voyage-3-large",
        input_type="document",
    )
    # C7: response is passed through unchanged.
    assert result.embeddings == [[0.11, 0.22, 0.33, 0.44]]
    assert result.total_tokens == 8

    assert len(captured) == 1
    signed = captured[0]
    receipt = signed["receipt"]
    assert receipt["schema"] == "embedding_inference/v1"
    assert receipt["deployer_id"] == "acme-eu-test"
    assert receipt["model"]["provider"] == "voyage"
    assert receipt["model"]["model_id"] == "voyage-3-large"
    assert receipt["model"]["input_type"] == "document"
    assert receipt["model"]["total_tokens"] == 8
    emb = receipt["embeddings"][0]
    assert emb["input_sha256_hex"] == hashlib.sha256(b"EU AI Act Article 50 text").hexdigest()
    assert emb["vector_dim"] == 4
    expected_vec_hash = hashlib.sha256(canonicalize_vector([0.11, 0.22, 0.33, 0.44])).hexdigest()
    assert emb["vector_sha256_hex"] == expected_vec_hash


def test_sync_embed_handles_string_input_not_list():
    captured: list = []
    fake_inner = MagicMock()
    fake_inner.embed.return_value = SimpleNamespace(embeddings=[[1.0, 2.0]], total_tokens=2)
    wrapper = LedgerProofVoyage(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )
    wrapper.embed(texts="single string", model="voyage-3-lite")
    receipt = captured[0]["receipt"]
    assert len(receipt["embeddings"]) == 1
    assert receipt["embeddings"][0]["input_sha256_hex"] == hashlib.sha256(b"single string").hexdigest()


def test_sync_rerank_emits_receipt():
    captured: list = []
    fake_inner = MagicMock()
    fake_inner.rerank.return_value = _fake_rerank_result()
    wrapper = LedgerProofVoyage(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )
    documents = ["article 50", "annex iv"]
    result = wrapper.rerank(
        query="What does Article 50 require?",
        documents=documents,
        model="rerank-2",
    )
    assert result.results[0].relevance_score == 0.94

    receipt = captured[0]["receipt"]
    assert receipt["schema"] == "rerank_inference/v1"
    assert receipt["rerank_query_sha256_hex"] == hashlib.sha256(
        b"What does Article 50 require?"
    ).hexdigest()
    assert len(receipt["rerank_results"]) == 2
    # First reranked is original_index=1 ("annex iv")
    assert receipt["rerank_results"][0]["original_index"] == 1
    assert receipt["rerank_results"][0]["document_sha256_hex"] == hashlib.sha256(b"annex iv").hexdigest()


def test_async_embed_emits_receipt():
    captured: list = []
    fake_inner = MagicMock()
    fake_inner.embed = AsyncMock(return_value=_fake_embed_result())
    wrapper = LedgerProofAsyncVoyage(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )

    async def _run():
        result = await wrapper.embed(
            texts=["async embed test"],
            model="voyage-3",
            input_type="query",
        )
        assert result.embeddings[0] == [0.11, 0.22, 0.33, 0.44]

    asyncio.run(_run())
    assert len(captured) == 1
    assert captured[0]["receipt"]["model"]["input_type"] == "query"


def test_async_rerank_emits_receipt():
    captured: list = []
    fake_inner = MagicMock()
    fake_inner.rerank = AsyncMock(return_value=_fake_rerank_result())
    wrapper = LedgerProofAsyncVoyage(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )

    async def _run():
        result = await wrapper.rerank(
            query="q?",
            documents=["a", "b"],
            model="rerank-2",
        )
        return result

    res = asyncio.run(_run())
    assert res.total_tokens == 15
    assert len(captured) == 1
    assert captured[0]["receipt"]["schema"] == "rerank_inference/v1"


def test_signature_verifies_with_published_public_key():
    """C4: offline verification works given the public key bytes."""
    captured: list = []
    signer = Ed25519Signer()
    fake_inner = MagicMock()
    fake_inner.embed.return_value = _fake_embed_result()
    wrapper = LedgerProofVoyage(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=signer,
    )
    wrapper.embed(texts=["verify me"], model="voyage-3-large", input_type="document")

    signed = captured[0]
    canonical_bytes = canonical_encode(signed["receipt"])
    sig = base64.b64decode(signed["signature_b64"])
    assert verify(signer.public_key_bytes(), canonical_bytes, sig)


def test_response_is_not_mutated_by_adapter():
    """C7: ensure the response object is the same instance after emission."""
    captured: list = []
    pre = _fake_embed_result()
    fake_inner = MagicMock()
    fake_inner.embed.return_value = pre

    wrapper = LedgerProofVoyage(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )
    post = wrapper.embed(texts=["ping"], model="voyage-3-large")
    assert post is pre
    assert not hasattr(post, "ledgerproof_receipt")
    assert not hasattr(post, "_lpr_receipt")


def test_attribute_passthrough_to_inner_client():
    """Non-intercepted methods (e.g. count_tokens, multimodal_embed) fall through."""
    fake_inner = MagicMock()
    fake_inner.count_tokens.return_value = 42
    wrapper = LedgerProofVoyage(
        deployer_id="acme-eu-test",
        client=fake_inner,
        signer=Ed25519Signer(),
    )
    assert wrapper.count_tokens(["hi"]) == 42
    fake_inner.count_tokens.assert_called_once()
