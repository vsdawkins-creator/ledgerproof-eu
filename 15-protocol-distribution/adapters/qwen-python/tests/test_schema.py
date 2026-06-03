"""Schema validation tests."""

from __future__ import annotations

import hashlib

import pytest
from pydantic import ValidationError

from ledgerproof_qwen.schema import (
    ChineseInferenceAttestation,
    ContentRef,
    CrossJurisdictionalRoute,
    ModelRef,
    ReceiptV1,
    RegulatoryContext,
    ToolUseRef,
    build_chatbot_session_receipt,
    build_cross_jurisdictional_routing_receipt,
    build_generated_content_receipt,
    build_multilingual_chinese_inference_receipt,
)


def _content_ref(text: str = "hello", role: str = "assistant") -> ContentRef:
    return ContentRef(
        sha256_hex=hashlib.sha256(text.encode()).hexdigest(),
        byte_length=len(text.encode()),
        role=role,
    )


def _model_ref() -> ModelRef:
    return ModelRef(model_id="qwen-max", response_id="req-test-123")


def _reg_ctx() -> RegulatoryContext:
    return RegulatoryContext(
        article_50_paragraph="1",
        deployer_jurisdiction="DE",
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
    assert payload["adapter"] == "ledgerproof-qwen"
    assert payload["model"]["provider"] == "qwen"
    assert payload["model"]["model_id"] == "qwen-max"


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


def test_multilingual_chinese_inference_receipt_carries_attestation():
    att = ChineseInferenceAttestation(
        chinese_disclosure_shown=True,
        chinese_disclosure_text_hash_sha256_hex=hashlib.sha256("此为AI生成内容".encode()).hexdigest(),
        endpoint_region="singapore",
        avoids_mainland_residency=True,
        provider_legal_entity="Alibaba Cloud (Singapore) Private Limited",
    )
    r = build_multilingual_chinese_inference_receipt(
        receipt_id="rcpt_003",
        deployer_id="acme-eu",
        model=_model_ref(),
        content_refs=[_content_ref()],
        regulatory_context=_reg_ctx(),
        chinese_inference=att,
    )
    payload = r.to_payload()
    assert payload["schema"] == "multilingual_chinese_inference/v1"
    assert payload["chinese_inference"]["endpoint_region"] == "singapore"
    assert payload["chinese_inference"]["avoids_mainland_residency"] is True
    assert payload["chinese_inference"]["chinese_disclosure_shown"] is True


def test_cross_jurisdictional_routing_receipt_carries_route():
    route = CrossJurisdictionalRoute(
        endpoint_region="singapore",
        endpoint_base_url="https://dashscope-intl.aliyuncs.com",
        avoids_mainland_residency=True,
        transfer_mechanism="SCCs-2021/914 + supplementary measures",
        provider_legal_entity="Alibaba Cloud (Singapore) Private Limited",
        notes="Inference routed via Singapore endpoint to support GDPR Schrems-II analysis.",
    )
    r = build_cross_jurisdictional_routing_receipt(
        receipt_id="rcpt_004",
        deployer_id="acme-eu",
        model=_model_ref(),
        content_refs=[_content_ref()],
        regulatory_context=_reg_ctx(),
        cross_jurisdictional_route=route,
    )
    payload = r.to_payload()
    assert payload["schema"] == "cross_jurisdictional_routing/v1"
    assert payload["cross_jurisdictional_route"]["endpoint_region"] == "singapore"
    assert (
        payload["cross_jurisdictional_route"]["endpoint_base_url"]
        == "https://dashscope-intl.aliyuncs.com"
    )
    assert payload["cross_jurisdictional_route"]["avoids_mainland_residency"] is True


def test_cross_jurisdictional_route_rejects_non_http_url():
    with pytest.raises(ValidationError):
        CrossJurisdictionalRoute(
            endpoint_region="singapore",
            endpoint_base_url="dashscope-intl.aliyuncs.com",  # no scheme
            avoids_mainland_residency=True,
        )


def test_receipt_requires_at_least_one_content_ref():
    with pytest.raises(ValidationError):
        ReceiptV1(
            schema="chatbot_session/v1",
            receipt_id="rcpt_005",
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
            receipt_id="rcpt_006",
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
            receipt_id="rcpt_007",
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
            receipt_id="rcpt_008",
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
            receipt_id="rcpt_009",
            deployer_id="acme-eu",
            model=_model_ref(),
            content_refs=[_content_ref()],
            regulatory_context=_reg_ctx(),
            free_text_prompt="this should be rejected",  # type: ignore[call-arg]
        )


def test_chinese_inference_endpoint_region_constrained():
    """The endpoint_region enum should reject arbitrary strings."""
    with pytest.raises(ValidationError):
        ChineseInferenceAttestation(
            chinese_disclosure_shown=True,
            endpoint_region="moon-base",  # type: ignore[arg-type]
            avoids_mainland_residency=True,
        )
