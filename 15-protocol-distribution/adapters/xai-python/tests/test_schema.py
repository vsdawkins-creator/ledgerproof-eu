"""Schema validation tests — including Grok-specific schemas."""

import hashlib

import pytest
from pydantic import ValidationError

from ledgerproof_xai.schema import (
    ChatbotSessionV1,
    GeneratedContentV1,
    RealtimeDataInferenceV1,
    VisionInferenceV1,
    build_receipt,
)


_PROMPT_HASH = hashlib.sha256(b"hi").hexdigest()
_RESPONSE_HASH = hashlib.sha256(b"hello").hexdigest()
_SOURCES_HASH = hashlib.sha256(b"https://x.com/abc").hexdigest()
_IMAGE_HASH = hashlib.sha256(b"PNGdata").hexdigest()


def _base_fields(**overrides):
    fields = dict(
        deployer_id="urn:eu:deployer:acme",
        model_id="grok-2-latest",
        interaction_id="grok-cmpl-123",
        prompt_sha256=_PROMPT_HASH,
        response_sha256=_RESPONSE_HASH,
    )
    fields.update(overrides)
    return fields


def test_chatbot_session_v1_happy_path():
    r = ChatbotSessionV1(**_base_fields())
    assert r.schema_id == "chatbot_session/v1"
    assert r.article_basis == "EU_AI_Act_Art_50_1"
    assert r.model_provider == "xai"


def test_generated_content_v1_happy_path():
    r = GeneratedContentV1(**_base_fields(), content_modality="text")
    assert r.schema_id == "generated_content/v1"
    assert r.content_modality == "text"
    assert r.machine_readable_marker is True


def test_realtime_data_inference_v1_with_sources_hash():
    r = RealtimeDataInferenceV1(
        **_base_fields(),
        realtime_data_used=True,
        realtime_sources_sha256=_SOURCES_HASH,
        public_interest_text=True,
    )
    assert r.schema_id == "realtime_data_inference/v1"
    assert r.realtime_data_used is True
    assert r.realtime_sources_sha256 == _SOURCES_HASH
    assert r.public_interest_text is True


def test_realtime_data_inference_v1_rejects_bad_sources_hash():
    with pytest.raises(ValidationError):
        RealtimeDataInferenceV1(
            **_base_fields(),
            realtime_data_used=True,
            realtime_sources_sha256="not-a-hash",
        )


def test_vision_inference_v1_with_image_hash():
    r = VisionInferenceV1(
        **_base_fields(),
        image_input_sha256=_IMAGE_HASH,
        image_count=2,
        content_modality="image",
    )
    assert r.schema_id == "vision_inference/v1"
    assert r.image_input_sha256 == _IMAGE_HASH
    assert r.image_count == 2


def test_vision_inference_v1_rejects_bad_image_hash():
    with pytest.raises(ValidationError):
        VisionInferenceV1(
            **_base_fields(),
            image_input_sha256="zzz",
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
        build_receipt("realtime_data_inference/v1", **_base_fields()),
        RealtimeDataInferenceV1,
    )
    assert isinstance(
        build_receipt("vision_inference/v1", **_base_fields()),
        VisionInferenceV1,
    )
    with pytest.raises(ValueError):
        build_receipt("nope/v1", **_base_fields())
