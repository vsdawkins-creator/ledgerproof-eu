"""Manual emit + helper tests for Voyage adapter."""

from __future__ import annotations

import hashlib
from types import SimpleNamespace

from ledgerproof_voyage import (
    QueueEmitter,
    emit_embedding_receipt,
    emit_rag_pipeline_receipt,
    emit_rerank_receipt,
)
from ledgerproof_voyage.canonical import canonicalize_vector
from ledgerproof_voyage.manual import (
    build_embedding_refs,
    build_rerank_result_refs,
    build_voyage_model_ref,
    extract_embeddings,
    extract_rerank_results,
    extract_total_tokens,
)
from ledgerproof_voyage.signer import Ed25519Signer


def _fake_embed_result(vectors=None, total_tokens=42):
    return SimpleNamespace(
        embeddings=vectors or [[0.1, 0.2, 0.3, 0.4], [0.5, 0.6, 0.7, 0.8]],
        total_tokens=total_tokens,
    )


def _fake_rerank_result(items=None, total_tokens=10):
    return SimpleNamespace(
        results=items
        or [
            SimpleNamespace(index=1, document="second doc", relevance_score=0.92),
            SimpleNamespace(index=0, document="first doc", relevance_score=0.34),
        ],
        total_tokens=total_tokens,
    )


def test_extract_embeddings_object_shape():
    out = extract_embeddings(_fake_embed_result())
    assert out == [[0.1, 0.2, 0.3, 0.4], [0.5, 0.6, 0.7, 0.8]]


def test_extract_embeddings_dict_shape():
    out = extract_embeddings({"embeddings": [[1.0, 2.0]]})
    assert out == [[1.0, 2.0]]


def test_extract_total_tokens():
    assert extract_total_tokens(_fake_embed_result(total_tokens=7)) == 7
    assert extract_total_tokens({"total_tokens": 11}) == 11
    assert extract_total_tokens(None) is None


def test_extract_rerank_results():
    results = extract_rerank_results(_fake_rerank_result())
    assert len(results) == 2
    assert results[0].relevance_score == 0.92


def test_build_embedding_refs_hashes_input_and_vector():
    inputs = ["hello", "world"]
    vectors = [[1.0, 2.0], [3.0, 4.0]]
    refs = build_embedding_refs(inputs, vectors)
    assert len(refs) == 2
    assert refs[0].input_sha256_hex == hashlib.sha256(b"hello").hexdigest()
    assert refs[0].vector_sha256_hex == hashlib.sha256(canonicalize_vector([1.0, 2.0])).hexdigest()
    assert refs[0].vector_dim == 2
    assert refs[1].input_index == 1


def test_build_embedding_refs_rejects_length_mismatch():
    import pytest

    with pytest.raises(ValueError):
        build_embedding_refs(["a", "b"], [[1.0]])


def test_build_rerank_result_refs_binds_score_and_doc_hash():
    documents = ["alpha", "beta", "gamma"]
    voyage_results = [
        SimpleNamespace(index=2, relevance_score=0.99),
        SimpleNamespace(index=0, relevance_score=0.51),
    ]
    refs = build_rerank_result_refs(documents, voyage_results)
    assert refs[0].original_index == 2
    assert refs[0].rerank_position == 0
    assert refs[0].relevance_score == 0.99
    assert refs[0].document_sha256_hex == hashlib.sha256(b"gamma").hexdigest()
    assert refs[1].original_index == 0
    assert refs[1].document_sha256_hex == hashlib.sha256(b"alpha").hexdigest()


def test_build_rerank_result_refs_clamps_out_of_range_scores():
    """Defensive — even if Voyage returns a >1.0 score, we accept it as 1.0."""
    documents = ["a"]
    voyage_results = [SimpleNamespace(index=0, relevance_score=1.5)]
    refs = build_rerank_result_refs(documents, voyage_results)
    assert refs[0].relevance_score == 1.0


def test_build_voyage_model_ref_normalizes_input_type():
    mr = build_voyage_model_ref(model="voyage-3-large", input_type="document")
    assert mr.input_type == "document"
    mr2 = build_voyage_model_ref(model="voyage-3-large", input_type="bogus")
    assert mr2.input_type == "none"
    mr3 = build_voyage_model_ref(model="voyage-3-large")
    assert mr3.input_type is None


def test_emit_embedding_receipt_returns_signed_dict_and_emits():
    captured: list = []
    signed = emit_embedding_receipt(
        deployer_id="acme-eu",
        model="voyage-3-large",
        inputs=["doc1", "doc2"],
        result=_fake_embed_result(),
        input_type="document",
        signer=Ed25519Signer(),
        emitter=QueueEmitter(captured.append),
    )
    assert signed["signature_alg"] == "ed25519"
    assert len(captured) == 1
    receipt = captured[0]["receipt"]
    assert receipt["schema"] == "embedding_inference/v1"
    assert receipt["deployer_id"] == "acme-eu"
    assert receipt["model"]["input_type"] == "document"
    assert receipt["model"]["total_tokens"] == 42
    assert len(receipt["embeddings"]) == 2
    assert receipt["regulatory_context"]["article_50_paragraph"] == "supporting"


def test_emit_rerank_receipt_returns_signed_dict_and_emits():
    captured: list = []
    docs = ["first doc", "second doc"]
    signed = emit_rerank_receipt(
        deployer_id="acme-eu",
        model="rerank-2",
        query="what is article 50?",
        documents=docs,
        result=_fake_rerank_result(),
        document_ids=["doc-a", "doc-b"],
        signer=Ed25519Signer(),
        emitter=QueueEmitter(captured.append),
    )
    assert signed["signature_alg"] == "ed25519"
    receipt = captured[0]["receipt"]
    assert receipt["schema"] == "rerank_inference/v1"
    assert receipt["rerank_query_sha256_hex"] == hashlib.sha256(b"what is article 50?").hexdigest()
    assert receipt["rerank_results"][0]["relevance_score"] == 0.92
    assert receipt["rerank_results"][0]["document_id"] == "doc-b"


def test_emit_rag_pipeline_receipt_chains_upstream_and_downstream():
    captured: list = []
    upstream_emb = emit_embedding_receipt(
        deployer_id="acme-eu",
        model="voyage-3-large",
        inputs=["A", "B"],
        result=_fake_embed_result(),
        input_type="document",
        signer=Ed25519Signer(),
        emitter=QueueEmitter(captured.append),
    )
    upstream_rr = emit_rerank_receipt(
        deployer_id="acme-eu",
        model="rerank-2",
        query="q",
        documents=["A", "B"],
        result=_fake_rerank_result(),
        signer=Ed25519Signer(),
        emitter=QueueEmitter(captured.append),
    )

    # Forge a downstream chat-adapter signed receipt (would normally come from
    # ledgerproof-openai / ledgerproof-anthropic / ledgerproof-cohere etc.).
    downstream_signed = {
        "receipt": {
            "schema": "chatbot_session/v1",
            "receipt_id": "rcpt_chat_xyz",
            "deployer_id": "acme-eu",
            "model": {"provider": "openai", "model_id": "gpt-4o", "response_id": "r1"},
        },
        "signature_alg": "ed25519",
        "signature_b64": "AAAA",
        "signer_key_id": "lpr-ed25519-deadbeef",
    }

    signed = emit_rag_pipeline_receipt(
        deployer_id="acme-eu",
        upstream_signed_receipts=[upstream_emb, upstream_rr],
        downstream_signed_receipt=downstream_signed,
        downstream_adapter="ledgerproof-openai",
        user_query="what is article 50?",
        assistant_response="Article 50 requires...",
        signer=Ed25519Signer(),
        emitter=QueueEmitter(captured.append),
    )
    receipt = signed["receipt"]
    assert receipt["schema"] == "rag_pipeline_evidence/v1"
    assert receipt["regulatory_context"]["article_50_paragraph"] == "1"
    assert len(receipt["upstream_receipts"]) == 2
    schemas = {u["schema_name"] for u in receipt["upstream_receipts"]}
    assert schemas == {"embedding_inference/v1", "rerank_inference/v1"}
    assert receipt["downstream_chat"]["downstream_adapter"] == "ledgerproof-openai"
    assert receipt["downstream_chat"]["downstream_receipt_id"] == "rcpt_chat_xyz"


def test_emit_rag_pipeline_rejects_non_voyage_upstream_schema():
    import pytest

    bogus_upstream = {
        "receipt": {
            "schema": "chatbot_session/v1",  # not allowed as upstream
            "receipt_id": "x",
        }
    }
    downstream = {
        "receipt": {
            "schema": "chatbot_session/v1",
            "receipt_id": "y",
        }
    }
    with pytest.raises(ValueError):
        emit_rag_pipeline_receipt(
            deployer_id="acme-eu",
            upstream_signed_receipts=[bogus_upstream],
            downstream_signed_receipt=downstream,
            downstream_adapter="ledgerproof-openai",
            user_query="q",
        )
