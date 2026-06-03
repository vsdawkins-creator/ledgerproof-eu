"""Schema validation tests (Codestral-specific schemas)."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from ledgerproof_mistral_codestral.schema import (
    ContentRef,
    FimPositions,
    GeneratedCodeAttributes,
    ModelRef,
    ReceiptV1,
    RegulatoryContext,
    SafetyCriticalReview,
    ToolUseRef,
    build_chatbot_session_receipt,
    build_fim_completion_receipt,
    build_generated_code_receipt,
    build_safety_critical_code_review_receipt,
)


def _content_ref(text: str = "def fib():", role: str = "assistant") -> ContentRef:
    return ContentRef(
        sha256_hex=hashlib.sha256(text.encode()).hexdigest(),
        byte_length=len(text.encode()),
        role=role,
    )


def _model_ref() -> ModelRef:
    return ModelRef(model_id="codestral-latest", response_id="cmpl_cstr_001")


def _reg_ctx(para: str = "2") -> RegulatoryContext:
    return RegulatoryContext(
        article_50_paragraph=para,
        deployer_jurisdiction="FR",
        end_user_disclosure_made=True,
    )


def test_chatbot_session_receipt_round_trips():
    r = build_chatbot_session_receipt(
        receipt_id="rcpt_001",
        deployer_id="acme-eu",
        model=_model_ref(),
        content_refs=[_content_ref()],
        regulatory_context=_reg_ctx("1"),
    )
    payload = r.to_payload()
    assert payload["schema"] == "chatbot_session/v1"
    assert payload["adapter"] == "ledgerproof-mistral-codestral"
    assert payload["model"]["provider"] == "mistral-codestral"


def test_generated_code_receipt_carries_code_attributes():
    code_attrs = GeneratedCodeAttributes(
        language="python",
        line_count=12,
        has_security_pattern=False,
        static_analyser="bandit-1.7",
    )
    r = build_generated_code_receipt(
        receipt_id="rcpt_002",
        deployer_id="acme-eu",
        model=_model_ref(),
        content_refs=[_content_ref()],
        regulatory_context=_reg_ctx("2"),
        code_attributes=code_attrs,
    )
    payload = r.to_payload()
    assert payload["schema"] == "generated_code/v1"
    assert payload["code_attributes"]["language"] == "python"
    assert payload["code_attributes"]["line_count"] == 12
    assert payload["code_attributes"]["has_security_pattern"] is False
    assert payload["code_attributes"]["static_analyser"] == "bandit-1.7"


def test_fim_completion_receipt_carries_positions():
    refs = [
        _content_ref(role="prefix"),
        _content_ref(role="suffix"),
        _content_ref(role="middle"),
    ]
    fim = FimPositions(
        prefix_byte_length=100,
        suffix_byte_length=50,
        middle_byte_length=25,
    )
    r = build_fim_completion_receipt(
        receipt_id="rcpt_003",
        deployer_id="acme-eu",
        model=_model_ref(),
        content_refs=refs,
        regulatory_context=_reg_ctx("2"),
        fim_positions=fim,
    )
    payload = r.to_payload()
    assert payload["schema"] == "fim_completion/v1"
    assert payload["fim_positions"]["middle_byte_length"] == 25
    roles = [c["role"] for c in payload["content_refs"]]
    assert "prefix" in roles and "suffix" in roles and "middle" in roles


def test_safety_critical_code_review_receipt():
    review = SafetyCriticalReview(
        reviewer_id="reviewer-001",
        review_outcome="approved",
        review_completed_at=datetime.now(timezone.utc),
        review_policy_id="acme-secrev-policy-v3",
        deployed=True,
        deployment_target="prod-eu-west-3",
    )
    r = build_safety_critical_code_review_receipt(
        receipt_id="rcpt_004",
        deployer_id="acme-eu",
        model=_model_ref(),
        content_refs=[_content_ref()],
        regulatory_context=_reg_ctx("4"),
        code_attributes=GeneratedCodeAttributes(language="python", line_count=5),
        safety_review=review,
    )
    payload = r.to_payload()
    assert payload["schema"] == "safety_critical_code_review/v1"
    assert payload["safety_review"]["review_outcome"] == "approved"
    assert payload["safety_review"]["deployed"] is True


def test_safety_review_outcome_must_be_valid_literal():
    with pytest.raises(ValidationError):
        SafetyCriticalReview(
            reviewer_id="r1",
            review_outcome="lgtm",  # type: ignore[arg-type]
            review_completed_at=datetime.now(timezone.utc),
            review_policy_id="p1",
        )


def test_reviewer_id_rejects_email_shape_gdpr_guard():
    with pytest.raises(ValidationError) as exc_info:
        SafetyCriticalReview(
            reviewer_id="bob@example.com",
            review_outcome="approved",
            review_completed_at=datetime.now(timezone.utc),
            review_policy_id="p1",
        )
    assert "email" in str(exc_info.value).lower()


def test_receipt_requires_at_least_one_content_ref():
    with pytest.raises(ValidationError):
        ReceiptV1(
            schema="generated_code/v1",
            receipt_id="rcpt_005",
            deployer_id="acme-eu",
            model=_model_ref(),
            content_refs=[],
            regulatory_context=_reg_ctx(),
        )


def test_deployer_id_rejects_email_shape_gdpr_guard():
    with pytest.raises(ValidationError) as exc_info:
        ReceiptV1(
            schema="generated_code/v1",
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
            schema="generated_code/v1",
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
            schema="generated_code/v1",
            receipt_id="rcpt_008",
            deployer_id="bad deployer with spaces!",
            model=_model_ref(),
            content_refs=[_content_ref()],
            regulatory_context=_reg_ctx(),
        )


def test_tool_use_ref_validates_sha256_format():
    tu = ToolUseRef(
        tool_name="lint_python",
        tool_use_id="call_lint_1",
        input_sha256_hex=hashlib.sha256(b"{}").hexdigest(),
    )
    assert tu.tool_name == "lint_python"
    with pytest.raises(ValidationError):
        ToolUseRef(tool_name="x", tool_use_id="y", input_sha256_hex="nothex")


def test_content_ref_requires_valid_sha256_hex():
    with pytest.raises(ValidationError):
        ContentRef(sha256_hex="nothex", byte_length=0, role="user")


def test_content_ref_supports_fim_roles():
    # prefix/suffix/middle are valid FIM roles
    for role in ("prefix", "suffix", "middle"):
        ref = ContentRef(
            sha256_hex=hashlib.sha256(b"x").hexdigest(),
            byte_length=1,
            role=role,  # type: ignore[arg-type]
        )
        assert ref.role == role


def test_extra_fields_forbidden():
    with pytest.raises(ValidationError):
        ReceiptV1(
            schema="generated_code/v1",
            receipt_id="rcpt_009",
            deployer_id="acme-eu",
            model=_model_ref(),
            content_refs=[_content_ref()],
            regulatory_context=_reg_ctx(),
            raw_generated_code="def fib():...",  # type: ignore[call-arg]
        )


def test_generated_code_attributes_normalises_language():
    attrs = GeneratedCodeAttributes(language="Python", line_count=3)
    assert attrs.language == "python"


def test_generated_code_attributes_rejects_bad_language():
    with pytest.raises(ValidationError):
        GeneratedCodeAttributes(language="not a language!", line_count=0)
