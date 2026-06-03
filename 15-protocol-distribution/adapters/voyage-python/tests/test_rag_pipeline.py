"""
End-to-end-ish test of the rag_pipeline_evidence/v1 chain.

We mock Voyage embed + rerank, mock a downstream chat receipt (as if produced
by ledgerproof-openai), and verify the rag_pipeline_evidence/v1 receipt binds
upstream + downstream receipts by their canonical SHA-256 hashes.
"""

from __future__ import annotations

import base64
import hashlib
from types import SimpleNamespace
from unittest.mock import MagicMock

from ledgerproof_voyage import (
    LedgerProofVoyage,
    QueueEmitter,
    emit_rag_pipeline_receipt,
)
from ledgerproof_voyage.canonical import canonical_encode
from ledgerproof_voyage.signer import Ed25519Signer, verify


def _fake_embed_result():
    return SimpleNamespace(embeddings=[[0.1, 0.2, 0.3]], total_tokens=4)


def _fake_rerank_result():
    return SimpleNamespace(
        results=[
            SimpleNamespace(index=0, document="doc-a", relevance_score=0.88),
            SimpleNamespace(index=1, document="doc-b", relevance_score=0.55),
        ],
        total_tokens=8,
    )


def _stub_downstream_receipt(deployer_id="acme-eu-test"):
    """Build a plausible signed downstream chat receipt as another adapter would."""
    return {
        "receipt": {
            "schema": "chatbot_session/v1",
            "schema_version": 1,
            "receipt_id": "rcpt_chat_downstream",
            "deployer_id": deployer_id,
            "model": {"provider": "anthropic", "model_id": "claude-3-7", "response_id": "msg_x"},
        },
        "signature_alg": "ed25519",
        "signature_b64": "AAAA",
        "signer_key_id": "lpr-ed25519-stub",
        "canonical_encoding": "cbor-rfc8949-deterministic",
    }


def test_rag_pipeline_full_chain():
    captured: list = []
    signer = Ed25519Signer()

    # Mock Voyage client and run embed + rerank through the wrapper.
    fake_inner = MagicMock()
    fake_inner.embed.return_value = _fake_embed_result()
    fake_inner.rerank.return_value = _fake_rerank_result()

    wrapper = LedgerProofVoyage(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=signer,
    )

    wrapper.embed(texts=["doc-a body"], model="voyage-3-large", input_type="document")
    wrapper.rerank(
        query="What is Article 50?",
        documents=["doc-a body", "doc-b body"],
        model="rerank-2",
    )

    upstream_signed = list(captured)  # 2 signed receipts so far
    assert len(upstream_signed) == 2
    schemas = sorted(s["receipt"]["schema"] for s in upstream_signed)
    assert schemas == ["embedding_inference/v1", "rerank_inference/v1"]

    # Now stitch upstream + downstream via rag_pipeline_evidence/v1.
    downstream = _stub_downstream_receipt()
    rag_signed = emit_rag_pipeline_receipt(
        deployer_id="acme-eu-test",
        upstream_signed_receipts=upstream_signed,
        downstream_signed_receipt=downstream,
        downstream_adapter="ledgerproof-anthropic",
        user_query="What is Article 50?",
        assistant_response="Article 50 requires disclosure...",
        signer=signer,
        emitter=QueueEmitter(captured.append),
    )

    rag_receipt = rag_signed["receipt"]
    assert rag_receipt["schema"] == "rag_pipeline_evidence/v1"
    assert rag_receipt["regulatory_context"]["article_50_paragraph"] == "1"

    # Each upstream ref's canonical hash matches the SHA-256 of the upstream payload.
    upstream_refs = rag_receipt["upstream_receipts"]
    assert len(upstream_refs) == 2
    for ref, sr in zip(upstream_refs, upstream_signed):
        expected_hex = hashlib.sha256(canonical_encode(sr["receipt"])).hexdigest()
        assert ref["receipt_canonical_sha256_hex"] == expected_hex

    # Downstream ref's canonical hash matches the SHA-256 of the downstream payload.
    expected_down_hex = hashlib.sha256(canonical_encode(downstream["receipt"])).hexdigest()
    assert rag_receipt["downstream_chat"]["downstream_receipt_canonical_sha256_hex"] == expected_down_hex
    assert rag_receipt["downstream_chat"]["downstream_adapter"] == "ledgerproof-anthropic"
    assert rag_receipt["downstream_chat"]["user_query_sha256_hex"] == hashlib.sha256(
        b"What is Article 50?"
    ).hexdigest()

    # The rag receipt itself verifies offline (C4).
    canonical_bytes = canonical_encode(rag_receipt)
    sig = base64.b64decode(rag_signed["signature_b64"])
    assert verify(signer.public_key_bytes(), canonical_bytes, sig)


def test_rag_pipeline_evidence_paragraph_defaults_to_1():
    """rag_pipeline_evidence/v1 defaults to article_50_paragraph='1', not 'supporting'."""
    captured: list = []
    fake_inner = MagicMock()
    fake_inner.embed.return_value = _fake_embed_result()
    wrapper = LedgerProofVoyage(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )
    wrapper.embed(texts=["x"], model="voyage-3-large", input_type="document")

    rag_signed = emit_rag_pipeline_receipt(
        deployer_id="acme-eu-test",
        upstream_signed_receipts=[captured[0]],
        downstream_signed_receipt=_stub_downstream_receipt(),
        downstream_adapter="ledgerproof-openai",
        user_query="q",
    )
    assert rag_signed["receipt"]["regulatory_context"]["article_50_paragraph"] == "1"
