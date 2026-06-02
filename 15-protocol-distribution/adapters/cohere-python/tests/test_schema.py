"""Schema validation tests for Cohere adapter."""

from __future__ import annotations

import hashlib

import pytest
from pydantic import ValidationError

from ledgerproof_cohere.schema import (
    ContentRef,
    DisclosureRef,
    ModelRef,
    ReceiptV1,
    RegulatoryContext,
    RetrievedDocumentRef,
    ToolUseRef,
    build_chatbot_session_receipt,
    build_multilingual_disclosure_receipt,
    build_rag_response_receipt,
)


def _content_ref(text: str = "hello", role: str = "assistant") -> ContentRef:
    return ContentRef(
        sha256_hex=hashlib.sha256(text.encode()).hexdigest(),
        byte_length=len(text.encode()),
        role=role,
    )


def _model_ref() -> ModelRef:
    return ModelRef(model_id="command-a-03-2025", response_id="resp_test_123")


def _reg_ctx(para: str = "1") -> RegulatoryContext:
    return RegulatoryContext(
        article_50_paragraph=para,
        deployer_jurisdiction="DE",
        end_user_disclosure_made=True,
    )


def _doc_ref(text: str = "doc body") -> RetrievedDocumentRef:
    return RetrievedDocumentRef(
        document_id="doc-1",
        sha256_hex=hashlib.sha256(text.encode()).hexdigest(),
        byte_length=len(text.encode()),
        rerank_relevance_score=0.87,
        rerank_index=0,
    )


def _disclosure(text: str = "Sie chatten mit einer KI.", lang: str = "de-DE") -> DisclosureRef:
    return DisclosureRef(
        language_tag=lang,
        disclosure_sha256_hex=hashlib.sha256(text.encode()).hexdigest(),
        disclosure_byte_length=len(text.encode()),
        disclosure_channel="chat-ui",
    )


def test_chatbot_session_receipt_round_trips():
    r = build_chatbot_session_receipt(
        receipt_id="rcpt_001",
        deployer_id="acme-eu",
        model=_model_ref(),
        content_refs=[_content_ref()],
        regulatory_context=_reg_ctx(),
    )
    payload = r.to_payload()
    assert payload["schema"] == "chatbot_session/v1"
    assert payload["deployer_id"] == "acme-eu"
    assert payload["adapter"] == "ledgerproof-cohere"
    assert payload["model"]["provider"] == "cohere"


def test_receipt_requires_at_least_one_content_ref():
    with pytest.raises(ValidationError):
        ReceiptV1(
            schema="chatbot_session/v1",
            receipt_id="rcpt_002",
            deployer_id="acme-eu",
            model=_model_ref(),
            content_refs=[],
            regulatory_context=_reg_ctx(),
        )


def test_deployer_id_pattern_enforced():
    with pytest.raises(ValidationError):
        ReceiptV1(
            schema="chatbot_session/v1",
            receipt_id="rcpt_003",
            deployer_id="bad deployer id with spaces!",
            model=_model_ref(),
            content_refs=[_content_ref()],
            regulatory_context=_reg_ctx(),
        )


def test_rag_response_requires_retrieved_documents():
    with pytest.raises(ValueError):
        build_rag_response_receipt(
            receipt_id="rcpt_004",
            deployer_id="acme-eu",
            model=_model_ref(),
            content_refs=[_content_ref()],
            regulatory_context=_reg_ctx(),
            retrieved_documents=[],
        )


def test_rag_response_round_trips():
    r = build_rag_response_receipt(
        receipt_id="rcpt_005",
        deployer_id="acme-eu",
        model=_model_ref(),
        content_refs=[_content_ref()],
        regulatory_context=_reg_ctx(),
        retrieved_documents=[_doc_ref("annex IV"), _doc_ref("article 50 text")],
    )
    payload = r.to_payload()
    assert payload["schema"] == "rag_response/v1"
    assert len(payload["retrieved_documents"]) == 2
    assert payload["retrieved_documents"][0]["rerank_relevance_score"] == 0.87


def test_multilingual_disclosure_requires_disclosure():
    with pytest.raises(ValueError):
        build_multilingual_disclosure_receipt(
            receipt_id="rcpt_006",
            deployer_id="acme-eu",
            model=_model_ref(),
            content_refs=[_content_ref()],
            regulatory_context=_reg_ctx(),
        )


def test_multilingual_disclosure_round_trips_de_fr_it():
    for lang, text in [
        ("de-DE", "Sie chatten mit einer KI."),
        ("fr-FR", "Vous discutez avec une IA."),
        ("it-IT", "Stai chattando con un'IA."),
        ("nl", "U chat met een AI."),
    ]:
        r = build_multilingual_disclosure_receipt(
            receipt_id=f"rcpt_007_{lang.replace('-', '_')}",
            deployer_id="acme-eu",
            model=_model_ref(),
            content_refs=[_content_ref()],
            regulatory_context=_reg_ctx(),
            disclosure=_disclosure(text, lang),
        )
        payload = r.to_payload()
        assert payload["schema"] == "multilingual_disclosure/v1"
        assert payload["disclosure"]["language_tag"] == lang


def test_disclosure_rejects_invalid_language_tag():
    with pytest.raises(ValidationError):
        DisclosureRef(
            language_tag="not a tag!",
            disclosure_sha256_hex=hashlib.sha256(b"x").hexdigest(),
            disclosure_byte_length=1,
        )


def test_retrieved_document_ref_rejects_out_of_range_score():
    with pytest.raises(ValidationError):
        RetrievedDocumentRef(
            document_id="doc-1",
            sha256_hex=hashlib.sha256(b"x").hexdigest(),
            byte_length=1,
            rerank_relevance_score=1.5,
        )


def test_content_ref_requires_valid_sha256_hex():
    with pytest.raises(ValidationError):
        ContentRef(sha256_hex="nothex", byte_length=0, role="user")


def test_tool_use_ref_validates_hash():
    tu = ToolUseRef(
        tool_name="search_db",
        tool_call_id="tc_abc",
        input_sha256_hex=hashlib.sha256(b"{}").hexdigest(),
    )
    assert tu.tool_name == "search_db"
