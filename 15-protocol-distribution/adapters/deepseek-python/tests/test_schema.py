"""Schema validation tests — including DeepSeek-specific schemas."""

import hashlib

import pytest
from pydantic import ValidationError

from ledgerproof_deepseek.schema import (
    ChatbotSessionV1,
    CodeGenerationV1,
    GeneratedContentV1,
    ReasoningTraceV1,
    build_receipt,
)


_PROMPT_HASH = hashlib.sha256(b"hi").hexdigest()
_RESPONSE_HASH = hashlib.sha256(b"hello").hexdigest()
_REASONING_HASH = hashlib.sha256(b"chain-of-thought").hexdigest()


def _base_fields(**overrides):
    fields = dict(
        deployer_id="urn:eu:deployer:acme",
        model_id="deepseek-chat",
        interaction_id="ds-cmpl-123",
        prompt_sha256=_PROMPT_HASH,
        response_sha256=_RESPONSE_HASH,
    )
    fields.update(overrides)
    return fields


def test_chatbot_session_v1_happy_path():
    r = ChatbotSessionV1(**_base_fields())
    assert r.schema_id == "chatbot_session/v1"
    assert r.article_basis == "EU_AI_Act_Art_50_1"
    assert r.model_provider == "deepseek"


def test_generated_content_v1_happy_path():
    r = GeneratedContentV1(**_base_fields(), content_modality="text")
    assert r.schema_id == "generated_content/v1"
    assert r.content_modality == "text"
    assert r.machine_readable_marker is True


def test_reasoning_trace_v1_with_reasoning_hash():
    r = ReasoningTraceV1(
        **_base_fields(model_id="deepseek-reasoner"),
        reasoning_sha256=_REASONING_HASH,
        reasoning_token_count=512,
        trace_surfaced_to_user=True,
    )
    assert r.schema_id == "reasoning_trace/v1"
    assert r.reasoning_sha256 == _REASONING_HASH
    assert r.reasoning_token_count == 512
    assert r.trace_surfaced_to_user is True


def test_reasoning_trace_v1_rejects_bad_reasoning_hash():
    with pytest.raises(ValidationError):
        ReasoningTraceV1(
            **_base_fields(model_id="deepseek-reasoner"),
            reasoning_sha256="zzz",
        )


def test_reasoning_trace_v1_allows_missing_reasoning_hash():
    """When the pipeline discards the trace, schema still validates."""
    r = ReasoningTraceV1(**_base_fields(model_id="deepseek-reasoner"))
    assert r.reasoning_sha256 is None


def test_code_generation_v1_happy_path():
    r = CodeGenerationV1(
        **_base_fields(model_id="deepseek-coder"),
        programming_language="python",
    )
    assert r.schema_id == "code_generation/v1"
    assert r.content_modality == "code"
    assert r.programming_language == "python"
    assert r.machine_readable_marker is True


def test_user_pseudonym_rejects_raw_email():
    """GDPR Art. 5(1)(c) — data minimization."""
    with pytest.raises(ValidationError):
        ChatbotSessionV1(**_base_fields(user_pseudonym="alice@example.com"))


def test_user_pseudonym_accepts_hash():
    r = ChatbotSessionV1(
        **_base_fields(user_pseudonym=hashlib.sha256(b"alice").hexdigest())
    )
    assert r.user_pseudonym is not None


def test_session_id_rejects_raw_email():
    """GDPR: session_id is a correlation ID, not user PII."""
    with pytest.raises(ValidationError):
        ChatbotSessionV1(**_base_fields(session_id="bob@example.com"))


def test_session_id_accepts_opaque_id():
    r = ChatbotSessionV1(**_base_fields(session_id="sess-abc-123"))
    assert r.session_id == "sess-abc-123"


def test_invalid_prompt_hash_rejected():
    with pytest.raises(ValidationError):
        ChatbotSessionV1(**_base_fields(prompt_sha256="not-a-hash"))


def test_deployer_id_must_be_urn():
    with pytest.raises(ValidationError):
        ChatbotSessionV1(**_base_fields(deployer_id="acme"))


def test_deployer_id_rejects_email():
    """GDPR — deployer_id is org-level identity, must not be a personal email."""
    with pytest.raises(ValidationError):
        ChatbotSessionV1(**_base_fields(deployer_id="founder@acme.example.com"))


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
        build_receipt(
            "reasoning_trace/v1", **_base_fields(model_id="deepseek-reasoner")
        ),
        ReasoningTraceV1,
    )
    assert isinstance(
        build_receipt(
            "code_generation/v1", **_base_fields(model_id="deepseek-coder")
        ),
        CodeGenerationV1,
    )
    with pytest.raises(ValueError):
        build_receipt("nope/v1", **_base_fields())
