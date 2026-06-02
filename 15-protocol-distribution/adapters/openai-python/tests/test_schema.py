"""Schema validation tests."""

import hashlib

import pytest
from pydantic import ValidationError

from ledgerproof_openai.schema import (
    AssistantResponseV1,
    ChatbotSessionV1,
    GeneratedContentV1,
    build_receipt,
)


_PROMPT_HASH = hashlib.sha256(b"hi").hexdigest()
_RESPONSE_HASH = hashlib.sha256(b"hello").hexdigest()


def _base_fields(**overrides):
    fields = dict(
        deployer_id="urn:eu:deployer:acme",
        model_id="gpt-4o",
        interaction_id="chatcmpl-123",
        prompt_sha256=_PROMPT_HASH,
        response_sha256=_RESPONSE_HASH,
    )
    fields.update(overrides)
    return fields


def test_chatbot_session_v1_happy_path():
    r = ChatbotSessionV1(**_base_fields())
    assert r.schema_id == "chatbot_session/v1"
    assert r.article_basis == "EU_AI_Act_Art_50_1"


def test_generated_content_v1_happy_path():
    r = GeneratedContentV1(**_base_fields(), content_modality="image")
    assert r.schema_id == "generated_content/v1"
    assert r.content_modality == "image"


def test_assistant_response_v1_requires_assistant_id():
    with pytest.raises(ValidationError):
        AssistantResponseV1(**_base_fields())
    r = AssistantResponseV1(**_base_fields(), assistant_id="asst_abc")
    assert r.assistant_id == "asst_abc"


def test_user_pseudonym_rejects_raw_email():
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


def test_build_receipt_dispatch():
    r = build_receipt("generated_content/v1", **_base_fields())
    assert isinstance(r, GeneratedContentV1)
    with pytest.raises(ValueError):
        build_receipt("nope/v1", **_base_fields())
