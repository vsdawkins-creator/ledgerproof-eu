"""Schema validation tests for the Voyage adapter."""

from __future__ import annotations

import hashlib

import pytest
from pydantic import ValidationError

from ledgerproof_voyage.schema import (
    DownstreamChatRef,
    EmbeddingRef,
    ReceiptV1,
    RegulatoryContext,
    RerankResultRef,
    UpstreamReceiptRef,
    VoyageModelRef,
    build_embedding_inference_receipt,
    build_rag_pipeline_evidence_receipt,
    build_rerank_inference_receipt,
)


def _h(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _model_ref() -> VoyageModelRef:
    return VoyageModelRef(
        model_id="voyage-3-large",
        response_id="voyage-resp-1",
        input_type="document",
        total_tokens=42,
    )


def _reg_ctx(para: str = "supporting") -> RegulatoryContext:
    return RegulatoryContext(
        article_50_paragraph=para,
        deployer_jurisdiction="DE",
        end_user_disclosure_made=True,
    )


def _embedding_ref(text: str = "hello", dim: int = 4, idx: int = 0) -> EmbeddingRef:
    return EmbeddingRef(
        input_sha256_hex=_h(text.encode()),
        input_byte_length=len(text.encode()),
        vector_sha256_hex=_h(b"\x00" * dim * 8),
        vector_dim=dim,
        input_index=idx,
    )


def _rerank_result_ref(text: str = "doc 1", pos: int = 0, score: float = 0.9) -> RerankResultRef:
    return RerankResultRef(
        document_id=f"doc-{pos}",
        document_sha256_hex=_h(text.encode()),
        document_byte_length=len(text.encode()),
        original_index=pos,
        rerank_position=pos,
        relevance_score=score,
    )


def test_embedding_inference_round_trips():
    r = build_embedding_inference_receipt(
        receipt_id="rcpt_emb_001",
        deployer_id="acme-eu",
        model=_model_ref(),
        regulatory_context=_reg_ctx("supporting"),
        embeddings=[_embedding_ref("doc body")],
    )
    payload = r.to_payload()
    assert payload["schema"] == "embedding_inference/v1"
    assert payload["deployer_id"] == "acme-eu"
    assert payload["adapter"] == "ledgerproof-voyage"
    assert payload["model"]["provider"] == "voyage"
    assert payload["embeddings"][0]["vector_dim"] == 4


def test_embedding_inference_requires_at_least_one_embedding():
    with pytest.raises(ValueError):
        build_embedding_inference_receipt(
            receipt_id="rcpt_emb_empty",
            deployer_id="acme-eu",
            model=_model_ref(),
            regulatory_context=_reg_ctx(),
            embeddings=[],
        )


def test_rerank_inference_round_trips():
    r = build_rerank_inference_receipt(
        receipt_id="rcpt_rerank_001",
        deployer_id="acme-eu",
        model=VoyageModelRef(model_id="rerank-2", response_id="voyage-rr-1"),
        regulatory_context=_reg_ctx("supporting"),
        rerank_query_sha256_hex=_h(b"what is article 50?"),
        rerank_query_byte_length=len(b"what is article 50?"),
        rerank_results=[
            _rerank_result_ref("doc A", pos=0, score=0.95),
            _rerank_result_ref("doc B", pos=1, score=0.42),
        ],
    )
    payload = r.to_payload()
    assert payload["schema"] == "rerank_inference/v1"
    assert len(payload["rerank_results"]) == 2
    assert payload["rerank_results"][0]["relevance_score"] == 0.95


def test_rerank_inference_requires_query_hash():
    with pytest.raises(ValueError):
        build_rerank_inference_receipt(
            receipt_id="rcpt_rerank_002",
            deployer_id="acme-eu",
            model=VoyageModelRef(model_id="rerank-2", response_id="voyage-rr-2"),
            regulatory_context=_reg_ctx(),
            rerank_results=[_rerank_result_ref()],
        )


def test_rerank_inference_requires_results():
    with pytest.raises(ValueError):
        build_rerank_inference_receipt(
            receipt_id="rcpt_rerank_003",
            deployer_id="acme-eu",
            model=VoyageModelRef(model_id="rerank-2", response_id="voyage-rr-3"),
            regulatory_context=_reg_ctx(),
            rerank_query_sha256_hex=_h(b"q"),
            rerank_query_byte_length=1,
            rerank_results=[],
        )


def test_rag_pipeline_evidence_requires_upstream_and_downstream():
    with pytest.raises(ValueError):
        build_rag_pipeline_evidence_receipt(
            receipt_id="rcpt_rag_001",
            deployer_id="acme-eu",
            model=VoyageModelRef(model_id="rag", response_id="rag-1"),
            regulatory_context=_reg_ctx("1"),
            upstream_receipts=[],
            downstream_chat=None,
        )


def test_rag_pipeline_evidence_round_trips():
    upstream = UpstreamReceiptRef(
        schema_name="embedding_inference/v1",
        receipt_id="rcpt_emb_001",
        receipt_canonical_sha256_hex=_h(b"upstream-payload"),
    )
    downstream = DownstreamChatRef(
        downstream_adapter="ledgerproof-openai",
        downstream_receipt_id="rcpt_chat_99",
        downstream_receipt_canonical_sha256_hex=_h(b"downstream-payload"),
        user_query_sha256_hex=_h(b"what is article 50?"),
        assistant_response_sha256_hex=_h(b"Article 50 requires disclosure..."),
    )
    r = build_rag_pipeline_evidence_receipt(
        receipt_id="rcpt_rag_002",
        deployer_id="acme-eu",
        model=VoyageModelRef(model_id="voyage-rag-pipeline", response_id="rag-2"),
        regulatory_context=_reg_ctx("1"),
        upstream_receipts=[upstream],
        downstream_chat=downstream,
    )
    payload = r.to_payload()
    assert payload["schema"] == "rag_pipeline_evidence/v1"
    assert payload["upstream_receipts"][0]["schema_name"] == "embedding_inference/v1"
    assert payload["downstream_chat"]["downstream_adapter"] == "ledgerproof-openai"


def test_deployer_id_pattern_enforced():
    with pytest.raises(ValidationError):
        ReceiptV1(
            schema="embedding_inference/v1",
            receipt_id="rcpt_001",
            deployer_id="bad id with spaces!",
            model=_model_ref(),
            regulatory_context=_reg_ctx(),
            embeddings=[_embedding_ref()],
        )


def test_rerank_result_rejects_out_of_range_score():
    with pytest.raises(ValidationError):
        RerankResultRef(
            document_sha256_hex=_h(b"x"),
            document_byte_length=1,
            original_index=0,
            rerank_position=0,
            relevance_score=1.7,
        )


def test_embedding_ref_requires_valid_sha256_hex():
    with pytest.raises(ValidationError):
        EmbeddingRef(
            input_sha256_hex="not-hex",
            input_byte_length=0,
            vector_sha256_hex=_h(b""),
            vector_dim=4,
            input_index=0,
        )


def test_embedding_ref_requires_positive_vector_dim():
    with pytest.raises(ValidationError):
        EmbeddingRef(
            input_sha256_hex=_h(b"x"),
            input_byte_length=1,
            vector_sha256_hex=_h(b""),
            vector_dim=0,
            input_index=0,
        )


def test_regulatory_context_accepts_supporting_paragraph():
    ctx = RegulatoryContext(
        article_50_paragraph="supporting",
        deployer_jurisdiction="FR",
        end_user_disclosure_made=False,
    )
    assert ctx.article_50_paragraph == "supporting"
