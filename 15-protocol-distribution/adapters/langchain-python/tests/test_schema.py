"""Schema validation tests for all three receipt variants."""

import pytest
from pydantic import ValidationError

from ledgerproof_langchain.schema import (
    SCHEMAS,
    ChatbotSessionReceipt,
    GeneratedContentReceipt,
    HumanReviewReceipt,
    get_schema,
)


_VALID_HEADER = {
    "run_id": "11111111-1111-1111-1111-111111111111",
    "timestamp_utc": "2026-06-01T12:00:00.000000Z",
    "deployer_id": "acme-corp-eu",
    "transcript_sha256": "a" * 64,
}


def test_chatbot_session_valid():
    r = ChatbotSessionReceipt(
        **_VALID_HEADER,
        model_identifier="gpt-4o-mini",
        disclosure_shown=True,
    )
    assert r.schema_id == "chatbot_session/v1"
    assert r.model_identifier == "gpt-4o-mini"


def test_generated_content_valid():
    r = GeneratedContentReceipt(
        **_VALID_HEADER,
        model_identifier="claude-opus-4-7",
        content_type="text/markdown",
        machine_readable_mark=True,
    )
    assert r.schema_id == "generated_content/v1"
    assert r.content_type == "text/markdown"


def test_human_review_valid():
    r = HumanReviewReceipt(
        **_VALID_HEADER,
        reviewer_id="reviewer-7421",
        reviewer_role="editor",
        review_rationale="Spot-checked for factual accuracy.",
        review_outcome="approved",
    )
    assert r.schema_id == "human_review/v1"
    assert r.review_outcome == "approved"


def test_deployer_id_rejects_email():
    with pytest.raises(ValidationError) as exc:
        ChatbotSessionReceipt(
            run_id=_VALID_HEADER["run_id"],
            timestamp_utc=_VALID_HEADER["timestamp_utc"],
            deployer_id="alice@corp.example",
            transcript_sha256=_VALID_HEADER["transcript_sha256"],
            model_identifier="gpt-4o-mini",
        )
    assert "GDPR" in str(exc.value) or "email" in str(exc.value).lower()


def test_reviewer_role_rejects_email():
    with pytest.raises(ValidationError):
        HumanReviewReceipt(
            **_VALID_HEADER,
            reviewer_id="reviewer-7421",
            reviewer_role="bob@corp.example",
        )


def test_review_rationale_rejects_email():
    with pytest.raises(ValidationError):
        HumanReviewReceipt(
            **_VALID_HEADER,
            reviewer_id="reviewer-7421",
            reviewer_role="editor",
            review_rationale="contact carol@corp.example",
        )


def test_transcript_sha256_must_be_hex64():
    with pytest.raises(ValidationError):
        ChatbotSessionReceipt(
            run_id=_VALID_HEADER["run_id"],
            timestamp_utc=_VALID_HEADER["timestamp_utc"],
            deployer_id="acme",
            transcript_sha256="not-a-hash",
            model_identifier="gpt-4o-mini",
        )


def test_get_schema_known():
    assert get_schema("chatbot_session/v1") is ChatbotSessionReceipt
    assert get_schema("generated_content/v1") is GeneratedContentReceipt
    assert get_schema("human_review/v1") is HumanReviewReceipt


def test_get_schema_unknown_raises():
    with pytest.raises(ValueError):
        get_schema("nope/v9")


def test_schemas_registry_complete():
    assert set(SCHEMAS.keys()) == {
        "chatbot_session/v1",
        "generated_content/v1",
        "human_review/v1",
    }
