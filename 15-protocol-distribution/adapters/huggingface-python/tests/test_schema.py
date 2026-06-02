"""Schema validation tests."""

import hashlib

import pytest
from pydantic import ValidationError

from ledgerproof_huggingface.schema import (
    ChatbotSessionV1,
    EUOpenModelHostedV1,
    GeneratedContentV1,
    LocalInferenceV1,
    build_receipt,
)


_PROMPT_HASH = hashlib.sha256(b"hi").hexdigest()
_RESPONSE_HASH = hashlib.sha256(b"hello").hexdigest()


def _base_fields(**overrides):
    fields = dict(
        deployer_id="urn:eu:deployer:acme",
        model_id="meta-llama/Llama-3.1-70B-Instruct",
        interaction_id="hf-123",
        prompt_sha256=_PROMPT_HASH,
        response_sha256=_RESPONSE_HASH,
    )
    fields.update(overrides)
    return fields


def test_chatbot_session_v1_happy_path():
    r = ChatbotSessionV1(**_base_fields())
    assert r.schema_id == "chatbot_session/v1"
    assert r.article_basis == "EU_AI_Act_Art_50_1"
    assert r.model_provider == "huggingface"


def test_generated_content_v1_happy_path():
    r = GeneratedContentV1(**_base_fields(), content_modality="image")
    assert r.schema_id == "generated_content/v1"
    assert r.content_modality == "image"


def test_eu_open_model_hosted_v1_carries_sovereignty_fields():
    r = EUOpenModelHostedV1(
        **_base_fields(),
        model_license="llama-3.1-community-license",
        open_weights=True,
    )
    assert r.schema_id == "eu_open_model_hosted/v1"
    assert r.hosting_platform == "huggingface_inference_api"
    assert r.hosting_provider_hq == "Paris/NYC"
    assert r.open_weights is True


def test_local_inference_v1_records_host_environment():
    env = {"hostname": "edge-node-fra-1", "platform": "Linux-6.x"}
    r = LocalInferenceV1(
        **_base_fields(),
        host_environment=env,
        device="cuda:0",
        task="text-generation",
    )
    assert r.schema_id == "local_inference/v1"
    assert r.host_environment["hostname"] == "edge-node-fra-1"
    assert r.framework == "transformers"
    assert r.device == "cuda:0"


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
    r = build_receipt("eu_open_model_hosted/v1", **_base_fields())
    assert isinstance(r, EUOpenModelHostedV1)
    with pytest.raises(ValueError):
        build_receipt("nope/v1", **_base_fields())
