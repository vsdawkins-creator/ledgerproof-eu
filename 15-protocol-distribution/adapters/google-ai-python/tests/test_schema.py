"""Schema invariants + GDPR validator tests."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from ledgerproof_google_ai.schema import (
    ContentRef,
    ModelRef,
    ReceiptV1,
    RegulatoryContext,
    build_chatbot_session_receipt,
    build_function_call_receipt,
    build_generated_content_receipt,
    build_multimodal_generation_receipt,
)


def _ok_model() -> ModelRef:
    return ModelRef(model_id="gemini-2.0-flash", response_id="resp-1")


def _ok_ctx() -> RegulatoryContext:
    return RegulatoryContext(
        article_50_paragraph="1",
        deployer_jurisdiction="EU",
        end_user_disclosure_made=True,
    )


def _ok_content_refs() -> list[ContentRef]:
    return [
        ContentRef(
            sha256_hex="a" * 64,
            byte_length=5,
            role="user",
        )
    ]


def test_chatbot_session_receipt_builds():
    r = build_chatbot_session_receipt(
        receipt_id="abc-123",
        deployer_id="acme-eu",
        model=_ok_model(),
        content_refs=_ok_content_refs(),
        regulatory_context=_ok_ctx(),
    )
    payload = r.to_payload()
    assert payload["schema"] == "chatbot_session/v1"
    assert payload["adapter"] == "ledgerproof-google-ai"


def test_generated_content_receipt_builds():
    r = build_generated_content_receipt(
        receipt_id="abc-123",
        deployer_id="acme-eu",
        model=_ok_model(),
        content_refs=_ok_content_refs(),
        regulatory_context=_ok_ctx(),
    )
    assert r.to_payload()["schema"] == "generated_content/v1"


def test_multimodal_generation_receipt_builds():
    r = build_multimodal_generation_receipt(
        receipt_id="abc-123",
        deployer_id="acme-eu",
        model=_ok_model(),
        content_refs=_ok_content_refs(),
        regulatory_context=_ok_ctx(),
        input_modalities=["text", "image"],
    )
    payload = r.to_payload()
    assert payload["schema"] == "multimodal_generation/v1"
    assert payload["input_modalities"] == ["text", "image"]


def test_function_call_receipt_builds():
    r = build_function_call_receipt(
        receipt_id="abc-123",
        deployer_id="acme-eu",
        model=_ok_model(),
        content_refs=_ok_content_refs(),
        regulatory_context=_ok_ctx(),
    )
    assert r.to_payload()["schema"] == "gemini_function_call/v1"


def test_deployer_id_rejects_email_shape():
    with pytest.raises(ValidationError) as exc:
        ReceiptV1(
            schema="chatbot_session/v1",
            receipt_id="abc",
            deployer_id="alice@example.com",
            model=_ok_model(),
            content_refs=_ok_content_refs(),
            regulatory_context=_ok_ctx(),
        )
    # The validator emits a specific GDPR-themed message.
    assert "email" in str(exc.value).lower() or "gdpr" in str(exc.value).lower()


def test_session_id_rejects_email_shape():
    with pytest.raises(ValidationError):
        ReceiptV1(
            schema="chatbot_session/v1",
            receipt_id="abc",
            deployer_id="acme-eu",
            session_id="bob@example.org",
            model=_ok_model(),
            content_refs=_ok_content_refs(),
            regulatory_context=_ok_ctx(),
        )


def test_session_id_accepts_opaque_id():
    r = ReceiptV1(
        schema="chatbot_session/v1",
        receipt_id="abc",
        deployer_id="acme-eu",
        session_id="sess_01HXXXXXXXXX",
        model=_ok_model(),
        content_refs=_ok_content_refs(),
        regulatory_context=_ok_ctx(),
    )
    assert r.session_id == "sess_01HXXXXXXXXX"


def test_content_refs_must_be_non_empty():
    with pytest.raises(ValidationError):
        ReceiptV1(
            schema="chatbot_session/v1",
            receipt_id="abc",
            deployer_id="acme-eu",
            model=_ok_model(),
            content_refs=[],
            regulatory_context=_ok_ctx(),
        )


def test_sha256_hex_format_enforced():
    with pytest.raises(ValidationError):
        ContentRef(sha256_hex="not-hex", byte_length=0, role="user")


def test_extra_fields_forbidden():
    with pytest.raises(ValidationError):
        ReceiptV1(
            schema="chatbot_session/v1",
            receipt_id="abc",
            deployer_id="acme-eu",
            model=_ok_model(),
            content_refs=_ok_content_refs(),
            regulatory_context=_ok_ctx(),
            unknown_extra_field="leaked",  # type: ignore[call-arg]
        )
