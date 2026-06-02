"""Schema validation tests."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from ledgerproof_replicate.schema import (
    ContentRef,
    InputRef,
    ModelRef,
    OutputArtifactRef,
    ReceiptV1,
    RegulatoryContext,
    build_chatbot_session_receipt,
    build_multimodel_attribution_receipt,
    build_synthetic_audio_receipt,
    build_synthetic_image_receipt,
    build_synthetic_video_receipt,
)


def _good_model(version: str | None = None) -> ModelRef:
    return ModelRef(
        model_id="black-forest-labs/flux-schnell",
        model_version=version,
        prediction_id="pred_abc",
    )


def _good_reg() -> RegulatoryContext:
    return RegulatoryContext(
        article_50_paragraph="2",
        deployer_jurisdiction="DE",
        end_user_disclosure_made=True,
    )


def _good_artifact() -> OutputArtifactRef:
    return OutputArtifactRef(
        sha256_hex="a" * 64,
        byte_length=4096,
        media_type="image/png",
        width_px=1024,
        height_px=1024,
    )


def test_model_ref_accepts_versioned_coordinate():
    m = ModelRef(
        model_id="stability-ai/sdxl",
        model_version="39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
        prediction_id="pred_xyz",
    )
    assert m.provider == "replicate"


def test_model_ref_rejects_bad_coordinate():
    with pytest.raises(ValidationError):
        ModelRef(model_id="not-a-valid-coord", prediction_id="x")


def test_content_ref_requires_lowercase_hex_sha256():
    with pytest.raises(ValidationError):
        ContentRef(sha256_hex="ZZZ", byte_length=1, role="output")


def test_input_ref_validates_type():
    r = InputRef(name="prompt", sha256_hex="a" * 64, byte_length=10, input_type="text")
    assert r.input_type == "text"


def test_synthetic_image_requires_output_artifact():
    with pytest.raises(ValueError):
        build_synthetic_image_receipt(
            receipt_id="r1",
            deployer_id="acme-eu",
            model=_good_model(),
            content_refs=[],
            input_refs=[],
            output_artifacts=[],
            regulatory_context=_good_reg(),
        )


def test_synthetic_image_happy_path():
    receipt = build_synthetic_image_receipt(
        receipt_id="r1",
        deployer_id="acme-eu",
        model=_good_model(),
        output_artifacts=[_good_artifact()],
        regulatory_context=_good_reg(),
    )
    assert receipt.schema_name == "synthetic_image/v1"


def test_synthetic_audio_requires_output_artifact():
    with pytest.raises(ValueError):
        build_synthetic_audio_receipt(
            receipt_id="r1",
            deployer_id="acme-eu",
            model=_good_model(),
            output_artifacts=[],
            regulatory_context=_good_reg(),
        )


def test_synthetic_video_requires_output_artifact():
    with pytest.raises(ValueError):
        build_synthetic_video_receipt(
            receipt_id="r1",
            deployer_id="acme-eu",
            model=_good_model(),
            output_artifacts=[],
            regulatory_context=_good_reg(),
        )


def test_chatbot_session_requires_content_ref():
    with pytest.raises(ValueError):
        build_chatbot_session_receipt(
            receipt_id="r1",
            deployer_id="acme-eu",
            model=_good_model(),
            content_refs=[],
            regulatory_context=_good_reg(),
        )


def test_multimodel_attribution_requires_version():
    with pytest.raises(ValueError):
        build_multimodel_attribution_receipt(
            receipt_id="r1",
            deployer_id="acme-eu",
            model=_good_model(version=None),
            output_artifacts=[_good_artifact()],
            regulatory_context=_good_reg(),
        )


def test_multimodel_attribution_with_version_ok():
    receipt = build_multimodel_attribution_receipt(
        receipt_id="r1",
        deployer_id="acme-eu",
        model=_good_model(version="abcdef0123456789"),
        output_artifacts=[_good_artifact()],
        regulatory_context=_good_reg(),
    )
    assert receipt.model.model_version == "abcdef0123456789"


def test_receipt_rejects_bad_deployer_id():
    with pytest.raises(ValidationError):
        ReceiptV1(
            schema="generated_content/v1",
            receipt_id="r1",
            deployer_id="acme eu with spaces",  # disallowed char
            model=_good_model(),
            content_refs=[ContentRef(sha256_hex="a" * 64, byte_length=1, role="output")],
            regulatory_context=_good_reg(),
        )


def test_regulatory_context_machine_readable_mark_optional():
    rc = RegulatoryContext(
        article_50_paragraph="2",
        deployer_jurisdiction="EU",
        end_user_disclosure_made=True,
        machine_readable_mark_applied=True,
    )
    assert rc.machine_readable_mark_applied is True


def test_output_artifact_video_fields():
    a = OutputArtifactRef(
        sha256_hex="a" * 64,
        byte_length=1_000_000,
        media_type="video/mp4",
        duration_seconds=3.5,
        frame_count=84,
        frames_per_second=24.0,
        width_px=576,
        height_px=320,
    )
    assert a.frame_count == 84
