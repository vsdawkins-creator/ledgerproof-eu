"""Schema validation tests — including Perplexity-specific schemas."""

import hashlib

import pytest
from pydantic import ValidationError

from ledgerproof_perplexity.schema import (
    AISearchWithCitationsV1,
    ChatbotSessionV1,
    GeneratedContentV1,
    PublicInterestTextV1,
    build_receipt,
)


_PROMPT_HASH = hashlib.sha256(b"hi").hexdigest()
_RESPONSE_HASH = hashlib.sha256(b"hello").hexdigest()
_CITATIONS_HASH = hashlib.sha256(b"[\"https://a.example/1\"]").hexdigest()


def _base_fields(**overrides):
    fields = dict(
        deployer_id="urn:eu:deployer:acme",
        model_id="sonar",
        interaction_id="pplx-cmpl-123",
        prompt_sha256=_PROMPT_HASH,
        response_sha256=_RESPONSE_HASH,
    )
    fields.update(overrides)
    return fields


def test_chatbot_session_v1_happy_path():
    r = ChatbotSessionV1(**_base_fields())
    assert r.schema_id == "chatbot_session/v1"
    assert r.article_basis == "EU_AI_Act_Art_50_1"
    assert r.model_provider == "perplexity"


def test_generated_content_v1_happy_path():
    r = GeneratedContentV1(**_base_fields(), content_modality="text")
    assert r.schema_id == "generated_content/v1"
    assert r.content_modality == "text"
    assert r.machine_readable_marker is True


def test_ai_search_with_citations_v1_happy_path():
    r = AISearchWithCitationsV1(
        **_base_fields(),
        citations_sha256=_CITATIONS_HASH,
        citations_count=3,
    )
    assert r.schema_id == "ai_search_with_citations/v1"
    assert r.article_basis == "EU_AI_Act_Art_50_1"
    assert r.citations_sha256 == _CITATIONS_HASH
    assert r.citations_count == 3
    assert r.search_used is True


def test_ai_search_with_citations_v1_rejects_bad_hash():
    with pytest.raises(ValidationError):
        AISearchWithCitationsV1(
            **_base_fields(),
            citations_sha256="not-a-hash",
            citations_count=1,
        )


def test_ai_search_with_citations_v1_rejects_negative_count():
    with pytest.raises(ValidationError):
        AISearchWithCitationsV1(
            **_base_fields(),
            citations_sha256=_CITATIONS_HASH,
            citations_count=-1,
        )


def test_public_interest_text_v1_happy_path():
    r = PublicInterestTextV1(
        **_base_fields(),
        citations_sha256=_CITATIONS_HASH,
        citations_count=4,
        disclosure_label_shown=True,
        editorial_review=False,
        subject_category="news.politics",
    )
    assert r.schema_id == "public_interest_text/v1"
    assert r.article_basis == "EU_AI_Act_Art_50_4"
    assert r.content_modality == "text"
    assert r.disclosure_label_shown is True
    assert r.editorial_review is False
    assert r.subject_category == "news.politics"


def test_public_interest_text_v1_rejects_bad_hash():
    with pytest.raises(ValidationError):
        PublicInterestTextV1(
            **_base_fields(),
            citations_sha256="zzz",
        )


def test_user_pseudonym_rejects_raw_email():
    """GDPR Art. 5(1)(c) — data minimization."""
    with pytest.raises(ValidationError):
        ChatbotSessionV1(**_base_fields(user_pseudonym="alice@example.com"))


def test_user_pseudonym_accepts_hash():
    r = ChatbotSessionV1(
        **_base_fields(user_pseudonym=hashlib.sha256(b"alice").hexdigest())
    )
    assert r.user_pseudonym is not None


def test_invalid_prompt_hash_rejected():
    with pytest.raises(ValidationError):
        ChatbotSessionV1(**_base_fields(prompt_sha256="not-a-hash"))


def test_deployer_id_must_be_urn():
    with pytest.raises(ValidationError):
        ChatbotSessionV1(**_base_fields(deployer_id="acme"))


def test_build_receipt_dispatch_all_schemas():
    assert isinstance(
        build_receipt("chatbot_session/v1", **_base_fields()),
        ChatbotSessionV1,
    )
    assert isinstance(
        build_receipt("generated_content/v1", **_base_fields()),
        GeneratedContentV1,
    )
    assert isinstance(
        build_receipt("ai_search_with_citations/v1", **_base_fields()),
        AISearchWithCitationsV1,
    )
    assert isinstance(
        build_receipt("public_interest_text/v1", **_base_fields()),
        PublicInterestTextV1,
    )
    with pytest.raises(ValueError):
        build_receipt("nope/v1", **_base_fields())
