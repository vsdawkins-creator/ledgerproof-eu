"""Schema validation tests (including multimodal + video schemas)."""

from __future__ import annotations

import hashlib

import pytest
from pydantic import ValidationError

from ledgerproof_reka.schema import (
    ContentRef,
    MediaRef,
    ModelRef,
    ReceiptV1,
    RegulatoryContext,
    ToolUseRef,
    build_chatbot_session_receipt,
    build_generated_content_receipt,
    build_multimodal_native_inference_receipt,
    build_video_understanding_receipt,
)


def _content_ref(text: str = "hello", role: str = "assistant", modality: str = "text") -> ContentRef:
    return ContentRef(
        sha256_hex=hashlib.sha256(text.encode()).hexdigest(),
        byte_length=len(text.encode()),
        role=role,
        modality=modality,
    )


def _model_ref() -> ModelRef:
    return ModelRef(model_id="reka-flash-3.1", response_id="resp_test_123")


def _reg_ctx() -> RegulatoryContext:
    return RegulatoryContext(
        article_50_paragraph="1",
        deployer_jurisdiction="DE",
        end_user_disclosure_made=True,
    )


def _media_ref(modality: str, mime: str) -> MediaRef:
    return MediaRef(
        sha256_hex=hashlib.sha256(b"fake-media").hexdigest(),
        byte_length=10,
        modality=modality,
        mime_type=mime,
        descriptor="1920x1080" if modality == "image" else None,
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
    assert payload["adapter"] == "ledgerproof-reka"
    assert payload["model"]["provider"] == "reka"


def test_generated_content_receipt_round_trips():
    r = build_generated_content_receipt(
        receipt_id="rcpt_gen_001",
        deployer_id="acme-eu",
        model=_model_ref(),
        content_refs=[_content_ref()],
        regulatory_context=_reg_ctx(),
    )
    assert r.to_payload()["schema"] == "generated_content/v1"


def test_multimodal_native_inference_receipt_binds_image_and_text():
    r = build_multimodal_native_inference_receipt(
        receipt_id="rcpt_mm_001",
        deployer_id="acme-eu",
        model=_model_ref(),
        content_refs=[
            _content_ref(text="describe this image", role="user", modality="text"),
            _content_ref(text="It depicts a sunset.", role="assistant", modality="text"),
        ],
        media_refs=[_media_ref("image", "image/png")],
        regulatory_context=_reg_ctx(),
        input_modalities=["text", "image"],
    )
    payload = r.to_payload()
    assert payload["schema"] == "multimodal_native_inference/v1"
    assert payload["input_modalities"] == ["text", "image"]
    assert payload["media_refs"][0]["modality"] == "image"
    assert payload["media_refs"][0]["mime_type"] == "image/png"


def test_video_understanding_receipt_binds_video_input():
    r = build_video_understanding_receipt(
        receipt_id="rcpt_vid_001",
        deployer_id="acme-eu",
        model=_model_ref(),
        content_refs=[_content_ref(text="describe the clip", role="user")],
        media_refs=[_media_ref("video", "video/mp4")],
        regulatory_context=_reg_ctx(),
        input_modalities=["video"],
    )
    payload = r.to_payload()
    assert payload["schema"] == "video_understanding/v1"
    assert "video" in payload["input_modalities"]
    assert payload["media_refs"][0]["modality"] == "video"


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


def test_input_modalities_rejects_empty():
    with pytest.raises(ValidationError):
        ReceiptV1(
            schema="multimodal_native_inference/v1",
            receipt_id="rcpt_004",
            deployer_id="acme-eu",
            model=_model_ref(),
            content_refs=[_content_ref()],
            regulatory_context=_reg_ctx(),
            input_modalities=[],
        )


def test_input_modalities_rejects_duplicates():
    with pytest.raises(ValidationError):
        ReceiptV1(
            schema="multimodal_native_inference/v1",
            receipt_id="rcpt_005",
            deployer_id="acme-eu",
            model=_model_ref(),
            content_refs=[_content_ref()],
            regulatory_context=_reg_ctx(),
            input_modalities=["text", "text"],
        )


def test_media_ref_rejects_malformed_mime():
    with pytest.raises(ValidationError):
        MediaRef(
            sha256_hex="a" * 64,
            byte_length=1,
            modality="image",
            mime_type="not-a-mime",
        )


def test_content_ref_requires_valid_sha256_hex():
    with pytest.raises(ValidationError):
        ContentRef(sha256_hex="nothex", byte_length=0, role="user")


def test_tool_use_ref_round_trips():
    tu = ToolUseRef(
        tool_name="bash",
        tool_use_id="tu_abc",
        input_sha256_hex=hashlib.sha256(b"{}").hexdigest(),
    )
    assert tu.tool_name == "bash"
