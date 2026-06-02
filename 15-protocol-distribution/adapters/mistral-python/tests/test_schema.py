"""Schema validation tests."""

from __future__ import annotations

import hashlib

import pytest
from pydantic import ValidationError

from ledgerproof_mistral.schema import (
    ContentRef,
    EuSovereigntyAttestation,
    ModelRef,
    ReceiptV1,
    RegulatoryContext,
    ToolUseRef,
    build_chatbot_session_receipt,
    build_eu_sovereign_ai_session_receipt,
    build_generated_content_receipt,
)


def _content_ref(text: str = "hello", role: str = "assistant") -> ContentRef:
    return ContentRef(
        sha256_hex=hashlib.sha256(text.encode()).hexdigest(),
        byte_length=len(text.encode()),
        role=role,
    )


def _model_ref() -> ModelRef:
    return ModelRef(model_id="mistral-large-latest", response_id="cmpl_test_123")


def _reg_ctx() -> RegulatoryContext:
    return RegulatoryContext(
        article_50_paragraph="1",
        deployer_jurisdiction="FR",
        end_user_disclosure_made=True,
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
    assert payload["adapter"] == "ledgerproof-mistral"
    assert payload["model"]["provider"] == "mistral"


def test_generated_content_receipt_uses_correct_schema_name():
    r = build_generated_content_receipt(
        receipt_id="rcpt_002",
        deployer_id="acme-eu",
        model=_model_ref(),
        content_refs=[_content_ref()],
        regulatory_context=RegulatoryContext(
            article_50_paragraph="2",
            deployer_jurisdiction="FR",
            end_user_disclosure_made=True,
        ),
    )
    payload = r.to_payload()
    assert payload["schema"] == "generated_content/v1"


def test_eu_sovereign_ai_session_receipt_carries_attestation():
    att = EuSovereigntyAttestation(
        inference_region="eu-west-3",
        eu_data_residency=True,
        eu_operated_infrastructure=True,
        provider_eu_headquartered=True,
        provider_legal_entity="Mistral AI SAS (Paris)",
    )
    r = build_eu_sovereign_ai_session_receipt(
        receipt_id="rcpt_003",
        deployer_id="acme-eu",
        model=_model_ref(),
        content_refs=[_content_ref()],
        regulatory_context=_reg_ctx(),
        eu_sovereignty=att,
    )
    payload = r.to_payload()
    assert payload["schema"] == "eu_sovereign_ai_session/v1"
    assert payload["eu_sovereignty"]["inference_region"] == "eu-west-3"
    assert payload["eu_sovereignty"]["provider_eu_headquartered"] is True


def test_receipt_requires_at_least_one_content_ref():
    with pytest.raises(ValidationError):
        ReceiptV1(
            schema="chatbot_session/v1",
            receipt_id="rcpt_004",
            deployer_id="acme-eu",
            model=_model_ref(),
            content_refs=[],
            regulatory_context=_reg_ctx(),
        )


def test_deployer_id_rejects_email_shape_gdpr_guard():
    """GDPR direct-identifier guard: deployer_id must not look like an email."""
    with pytest.raises(ValidationError) as exc_info:
        ReceiptV1(
            schema="chatbot_session/v1",
            receipt_id="rcpt_005",
            deployer_id="alice@example.com",
            model=_model_ref(),
            content_refs=[_content_ref()],
            regulatory_context=_reg_ctx(),
        )
    assert "email" in str(exc_info.value).lower()


def test_user_session_id_rejects_email_shape_gdpr_guard():
    with pytest.raises(ValidationError) as exc_info:
        ReceiptV1(
            schema="chatbot_session/v1",
            receipt_id="rcpt_006",
            deployer_id="acme-eu",
            user_session_id="bob.smith@example.org",
            model=_model_ref(),
            content_refs=[_content_ref()],
            regulatory_context=_reg_ctx(),
        )
    assert "email" in str(exc_info.value).lower()


def test_deployer_id_pattern_enforced():
    with pytest.raises(ValidationError):
        ReceiptV1(
            schema="chatbot_session/v1",
            receipt_id="rcpt_007",
            deployer_id="bad deployer id with spaces!",
            model=_model_ref(),
            content_refs=[_content_ref()],
            regulatory_context=_reg_ctx(),
        )


def test_tool_use_ref_validates_sha256_format():
    tu = ToolUseRef(
        tool_name="get_weather",
        tool_use_id="call_abc",
        input_sha256_hex=hashlib.sha256(b"{}").hexdigest(),
    )
    assert tu.tool_name == "get_weather"
    with pytest.raises(ValidationError):
        ToolUseRef(tool_name="x", tool_use_id="y", input_sha256_hex="nothex")


def test_content_ref_requires_valid_sha256_hex():
    with pytest.raises(ValidationError):
        ContentRef(sha256_hex="nothex", byte_length=0, role="user")


def test_extra_fields_forbidden():
    with pytest.raises(ValidationError):
        ReceiptV1(
            schema="chatbot_session/v1",
            receipt_id="rcpt_008",
            deployer_id="acme-eu",
            model=_model_ref(),
            content_refs=[_content_ref()],
            regulatory_context=_reg_ctx(),
            free_text_prompt="this should be rejected",  # type: ignore[call-arg]
        )
