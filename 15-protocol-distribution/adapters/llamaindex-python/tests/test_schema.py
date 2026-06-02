"""Schema validation tests — GDPR guards, required fields, hex constraints."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from ledgerproof_llamaindex.schema import (
    GeneratedContentReceipt,
    RagChatbotSessionReceipt,
    RagSynthesizedResponseReceipt,
    receipt_envelope,
)

ZERO = "0" * 64


def _base_rag_kwargs():
    return dict(
        receipt_id="r-00000001",
        deployer_id="acme-bank-eu",
        article="50(1)",
        session_id="sess-abcdef",
        model_provider="openai",
        model_name="gpt-4",
        retrieval_context_hash=ZERO,
        num_retrieved_chunks=0,
        transcript_hash=ZERO,
    )


def test_rag_chatbot_session_minimal_ok():
    r = RagChatbotSessionReceipt(**_base_rag_kwargs())
    assert r.schema_id == "rag_chatbot_session/v1"
    assert r.disclosure_shown is True


def test_rag_chatbot_session_rejects_email_in_subject():
    kwargs = _base_rag_kwargs()
    kwargs["subject_pseudonym"] = "alice@acme.eu"
    with pytest.raises(ValidationError):
        RagChatbotSessionReceipt(**kwargs)


def test_rag_chatbot_session_rejects_phone_in_deployer_id():
    kwargs = _base_rag_kwargs()
    kwargs["deployer_id"] = "+44 7700 900000"
    with pytest.raises(ValidationError):
        RagChatbotSessionReceipt(**kwargs)


def test_rag_chatbot_session_rejects_long_digit_national_id():
    kwargs = _base_rag_kwargs()
    kwargs["subject_pseudonym"] = "ID12345678"
    with pytest.raises(ValidationError):
        RagChatbotSessionReceipt(**kwargs)


def test_rag_chatbot_session_rejects_bad_article():
    kwargs = _base_rag_kwargs()
    kwargs["article"] = "9(2)"
    with pytest.raises(ValidationError):
        RagChatbotSessionReceipt(**kwargs)


def test_rag_chatbot_session_rejects_non_hex_transcript():
    kwargs = _base_rag_kwargs()
    kwargs["transcript_hash"] = "not-a-hash"
    with pytest.raises(ValidationError):
        RagChatbotSessionReceipt(**kwargs)


def test_generated_content_minimal_ok():
    r = GeneratedContentReceipt(
        receipt_id="r-content-1",
        deployer_id="acme",
        article="50(2)",
        content_kind="text",
        content_hash=ZERO,
        content_length_bytes=42,
        model_provider="openai",
        model_name="gpt-4",
    )
    assert r.marking_method == "transcript"


def test_rag_synthesized_response_validates_source_hashes():
    with pytest.raises(ValidationError):
        RagSynthesizedResponseReceipt(
            receipt_id="r-syn-1",
            deployer_id="acme",
            article="50(1)",
            session_id="sess-1234",
            query_hash=ZERO,
            response_hash=ZERO,
            source_document_hashes=["nope"],
            model_provider="openai",
            model_name="gpt-4",
        )


def test_receipt_envelope_shape():
    r = RagChatbotSessionReceipt(**_base_rag_kwargs())
    env = receipt_envelope(
        receipt=r,
        signature_hex="aa" * 64,
        public_key_hex="bb" * 32,
        key_id="lpr-test",
    )
    assert env["envelope_version"] == "lpr/0.1"
    assert env["signature"]["alg"] == "ed25519"
    assert env["signature"]["key_id"] == "lpr-test"
    assert env["payload"]["schema_id"] == "rag_chatbot_session/v1"
