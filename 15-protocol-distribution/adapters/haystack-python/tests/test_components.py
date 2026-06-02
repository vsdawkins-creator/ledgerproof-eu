"""Tests for LedgerProofComponent (works with or without haystack-ai)."""

import base64

from ledgerproof_haystack import (
    LedgerProofComponent,
    MemoryEmitter,
    canonical_cbor,
    generate_signing_key,
    verify_signature,
)


def test_component_emits_signed_receipt_default_schema():
    key = generate_signing_key()
    mem = MemoryEmitter()
    comp = LedgerProofComponent(
        signing_key=key,
        schema="haystack_node_receipt/v1",
        deployer="acme-de",
        emitter=mem,
        node_name="llm",
    )
    out = comp.run(content="Hallo Welt", query="Frage?")
    assert "receipt_id" in out
    assert "signature_b64" in out
    # passthrough preserved
    assert out["content"] == "Hallo Welt"
    assert len(mem) == 1


def test_component_signature_verifies():
    key = generate_signing_key()
    mem = MemoryEmitter()
    comp = LedgerProofComponent(
        signing_key=key,
        schema="generated_content/v1",
        deployer="acme-de",
        emitter=mem,
        model_id="gpt-4o-mini",
    )
    comp.run(content="Generated answer.")
    env = mem.records[0]
    sig = base64.b64decode(env["signature_b64"])
    assert verify_signature(env["public_key_b64"], canonical_cbor(env["receipt"]), sig)


def test_component_rag_session_schema():
    key = generate_signing_key()
    mem = MemoryEmitter()
    comp = LedgerProofComponent(
        signing_key=key,
        schema="rag_pipeline_session/v1",
        deployer="acme-de",
        emitter=mem,
        model_id="gpt-4o-mini",
        extra_fields={
            "pipeline_name": "german-rag",
            "component_count": 4,
            "retrieved_doc_count": 6,
        },
    )
    comp.run(content="Antwort", query="Was ist DSGVO?")
    env = mem.records[0]
    assert env["receipt"]["schema_id"] == "rag_pipeline_session/v1"
    assert env["receipt"]["pipeline_name"] == "german-rag"
    assert env["receipt"]["retrieved_doc_count"] == 6


def test_component_editorial_schema_with_reviewer():
    key = generate_signing_key()
    mem = MemoryEmitter()
    comp = LedgerProofComponent(
        signing_key=key,
        schema="editorial_pipeline_review/v1",
        deployer="news-de",
        emitter=mem,
        extra_fields={
            "public_interest_category": "news",
            "human_editorial_review": True,
            "reviewer_id": "editor-7",
            "review_decision": "published",
            "pipeline_name": "newsroom",
        },
    )
    comp.run(content="Story body...", query="Subject: EU AI Act")
    env = mem.records[0]
    assert env["receipt"]["reviewer_id"] == "editor-7"
    assert env["receipt"]["review_decision"] == "published"


def test_component_passthrough_does_not_mutate_input():
    key = generate_signing_key()
    mem = MemoryEmitter()
    comp = LedgerProofComponent(signing_key=key, emitter=mem, deployer="d")
    payload = ["a", "b", "c"]
    out = comp.run(content=payload)
    assert out["content"] is payload  # exact passthrough (C7)
