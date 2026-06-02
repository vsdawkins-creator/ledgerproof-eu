"""Schema validation tests."""

from __future__ import annotations

import hashlib

import pytest
from pydantic import ValidationError

from ledgerproof_together.schema import (
    ContentRef,
    ModelRef,
    OpenModelAttribution,
    ReceiptV1,
    RegulatoryContext,
    ToolUseRef,
    build_chatbot_session_receipt,
    build_generated_content_receipt,
    build_image_generation_receipt,
    build_open_model_inference_receipt,
    infer_open_model_attribution,
)


def _content_ref(text: str = "hello", role: str = "assistant") -> ContentRef:
    return ContentRef(
        sha256_hex=hashlib.sha256(text.encode()).hexdigest(),
        byte_length=len(text.encode()),
        role=role,
    )


def _model_ref(model_id: str = "meta-llama/Llama-3.3-70B-Instruct-Turbo") -> ModelRef:
    return ModelRef(model_id=model_id, response_id="cmpl_test_123")


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
    assert payload["adapter"] == "ledgerproof-together"
    assert payload["model"]["provider"] == "together"


def test_generated_content_receipt_uses_correct_schema_name():
    r = build_generated_content_receipt(
        receipt_id="rcpt_002",
        deployer_id="acme-eu",
        model=_model_ref(),
        content_refs=[_content_ref()],
        regulatory_context=RegulatoryContext(
            article_50_paragraph="2",
            deployer_jurisdiction="DE",
            end_user_disclosure_made=True,
        ),
    )
    payload = r.to_payload()
    assert payload["schema"] == "generated_content/v1"


def test_open_model_inference_receipt_carries_attribution():
    att = OpenModelAttribution(
        underlying_model_family="llama",
        underlying_model_provider="meta",
        host_provider="together",
        model_license="llama-3.3-community",
        weights_origin="https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct",
    )
    r = build_open_model_inference_receipt(
        receipt_id="rcpt_003",
        deployer_id="acme-eu",
        model=_model_ref(),
        content_refs=[_content_ref()],
        regulatory_context=_reg_ctx(),
        open_model=att,
    )
    payload = r.to_payload()
    assert payload["schema"] == "open_model_inference/v1"
    assert payload["open_model"]["underlying_model_family"] == "llama"
    assert payload["open_model"]["underlying_model_provider"] == "meta"
    assert payload["open_model"]["host_provider"] == "together"


def test_image_generation_receipt_supports_image_role():
    r = build_image_generation_receipt(
        receipt_id="rcpt_img_1",
        deployer_id="acme-eu",
        model=_model_ref("black-forest-labs/FLUX.1-schnell-Free"),
        content_refs=[
            _content_ref("a photo of a cat", role="user"),
            _content_ref("\x89PNG\r\n", role="image"),
        ],
        regulatory_context=RegulatoryContext(
            article_50_paragraph="2",
            deployer_jurisdiction="DE",
            end_user_disclosure_made=True,
        ),
        open_model=OpenModelAttribution(
            underlying_model_family="flux",
            underlying_model_provider="black-forest-labs",
        ),
    )
    payload = r.to_payload()
    assert payload["schema"] == "image_generation/v1"
    assert any(c["role"] == "image" for c in payload["content_refs"])


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


# ---------------------------------------------------------------------------
# infer_open_model_attribution — heuristic family/provider detection
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "model_id,expected_family,expected_provider",
    [
        ("meta-llama/Llama-3.3-70B-Instruct-Turbo", "llama", "meta"),
        ("meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo", "llama-vision", "meta"),
        ("mistralai/Mixtral-8x7B-Instruct-v0.1", "mixtral", "mistral-ai"),
        ("mistralai/Mistral-7B-Instruct-v0.3", "mistral", "mistral-ai"),
        ("Qwen/Qwen2.5-72B-Instruct-Turbo", "qwen", "alibaba-qwen"),
        ("Qwen/Qwen2-VL-72B-Instruct", "qwen-vision", "alibaba-qwen"),
        ("deepseek-ai/DeepSeek-R1", "deepseek-r1", "deepseek"),
        ("deepseek-ai/deepseek-llm-67b-chat", "deepseek", "deepseek"),
        ("google/gemma-2-27b-it", "gemma", "google"),
        ("microsoft/phi-3-mini-128k-instruct", "phi", "microsoft"),
        ("black-forest-labs/FLUX.1-schnell-Free", "flux", "black-forest-labs"),
    ],
)
def test_infer_open_model_attribution(model_id, expected_family, expected_provider):
    att = infer_open_model_attribution(model_id)
    assert att is not None, f"failed to infer for {model_id}"
    assert att.underlying_model_family == expected_family
    assert att.underlying_model_provider == expected_provider
    assert att.host_provider == "together"


def test_infer_open_model_attribution_returns_none_for_unknown():
    assert infer_open_model_attribution("some-unlisted/model-xyz") is None
    assert infer_open_model_attribution("") is None
