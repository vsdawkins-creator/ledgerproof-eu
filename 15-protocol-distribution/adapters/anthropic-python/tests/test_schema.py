"""Schema validation tests."""

from __future__ import annotations

import hashlib

import pytest
from pydantic import ValidationError

from ledgerproof_anthropic.schema import (
    ContentRef,
    ModelRef,
    ReceiptV1,
    RegulatoryContext,
    ToolUseRef,
    build_agent_action_receipt,
    build_chatbot_session_receipt,
)


def _content_ref(text: str = "hello", role: str = "assistant") -> ContentRef:
    return ContentRef(
        sha256_hex=hashlib.sha256(text.encode()).hexdigest(),
        byte_length=len(text.encode()),
        role=role,
    )


def _model_ref() -> ModelRef:
    return ModelRef(model_id="claude-opus-4-1", response_id="msg_test_123")


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
    assert payload["adapter"] == "ledgerproof-anthropic"


def test_receipt_requires_at_least_one_content_ref():
    with pytest.raises(ValidationError):
        ReceiptV1(
            schema="chatbot_session/v1",
            receipt_id="rcpt_002",
            deployer_id="acme-eu",
            model=_model_ref(),
            content_refs=[],
            regulatory_context=_reg_ctx(),
        )


def test_deployer_id_pattern_enforced():
    with pytest.raises(ValidationError):
        ReceiptV1(
            schema="chatbot_session/v1",
            receipt_id="rcpt_003",
            deployer_id="bad deployer id with spaces!",
            model=_model_ref(),
            content_refs=[_content_ref()],
            regulatory_context=_reg_ctx(),
        )


def test_agent_action_receipt_with_tool_use():
    tu = ToolUseRef(
        tool_name="bash",
        tool_use_id="tu_abc",
        input_sha256_hex=hashlib.sha256(b"{}").hexdigest(),
    )
    r = build_agent_action_receipt(
        receipt_id="rcpt_004",
        deployer_id="acme-eu",
        model=_model_ref(),
        content_refs=[_content_ref()],
        regulatory_context=_reg_ctx(),
        tool_uses=[tu],
    )
    payload = r.to_payload()
    assert payload["schema"] == "agent_action/v1"
    assert payload["tool_uses"][0]["tool_name"] == "bash"


def test_content_ref_requires_valid_sha256_hex():
    with pytest.raises(ValidationError):
        ContentRef(sha256_hex="nothex", byte_length=0, role="user")
