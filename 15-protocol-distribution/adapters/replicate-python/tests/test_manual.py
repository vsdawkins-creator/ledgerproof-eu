"""Manual emission tests."""

from __future__ import annotations

import base64
from types import SimpleNamespace

from ledgerproof_replicate import (
    QueueEmitter,
    emit_receipt,
    hash_audio_bytes,
    hash_image_bytes,
    hash_video_bytes,
    parse_model_coordinate,
)
from ledgerproof_replicate.canonical import canonical_encode
from ledgerproof_replicate.manual import (
    build_input_refs,
    build_model_ref_from_coordinate,
    build_model_ref_from_prediction,
)
from ledgerproof_replicate.signer import Ed25519Signer, verify


def test_parse_model_coordinate_with_version():
    a, v = parse_model_coordinate("stability-ai/sdxl:abc123")
    assert a == "stability-ai/sdxl"
    assert v == "abc123"


def test_parse_model_coordinate_without_version():
    a, v = parse_model_coordinate("meta/meta-llama-3-70b-instruct")
    assert a == "meta/meta-llama-3-70b-instruct"
    assert v is None


def test_build_model_ref_from_prediction_with_separate_fields():
    pred = SimpleNamespace(
        id="pred_xyz",
        model="black-forest-labs/flux-schnell",
        version="bf2f2e683d03a9549f484a37a0df1c4c08e8e3fa3a18f3e1c1d4a4dba8c0bc0e",
        status="succeeded",
        metrics=SimpleNamespace(predict_time=2.34),
    )
    ref = build_model_ref_from_prediction(pred)
    assert ref.model_id == "black-forest-labs/flux-schnell"
    assert ref.model_version.startswith("bf2f2e")
    assert ref.prediction_id == "pred_xyz"
    assert ref.predict_time_seconds == 2.34
    assert ref.status == "succeeded"


def test_build_input_refs_hashes_each_field():
    refs = build_input_refs(
        {"prompt": "a serene mountain lake", "guidance_scale": 7.5, "seed": 42}
    )
    names = {r.name for r in refs}
    assert names == {"prompt", "guidance_scale", "seed"}
    prompt_ref = next(r for r in refs if r.name == "prompt")
    assert prompt_ref.input_type == "text"
    assert prompt_ref.byte_length == len("a serene mountain lake".encode("utf-8"))
    seed_ref = next(r for r in refs if r.name == "seed")
    assert seed_ref.input_type == "number"


def test_build_input_refs_detects_file_url():
    refs = build_input_refs({"image": "https://example.com/in.png"})
    assert refs[0].input_type == "file"


def test_hash_image_bytes_builds_artifact():
    raw = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32
    a = hash_image_bytes(raw, width_px=512, height_px=512)
    assert a.media_type == "image/png"
    assert a.byte_length == len(raw)
    assert a.width_px == 512


def test_hash_audio_bytes_builds_artifact():
    raw = b"RIFF" + b"\x00" * 100
    a = hash_audio_bytes(raw, duration_seconds=2.5, sample_rate_hz=44100)
    assert a.media_type == "audio/wav"
    assert a.duration_seconds == 2.5


def test_hash_video_bytes_builds_artifact():
    raw = b"\x00" * 1000
    a = hash_video_bytes(raw, duration_seconds=4.0, frame_count=96, frames_per_second=24.0)
    assert a.frame_count == 96


def test_emit_receipt_signs_and_emits_synthetic_image():
    captured: list = []
    signer = Ed25519Signer()
    image = b"\x89PNG\r\n\x1a\nhello-world-fake-image"

    signed = emit_receipt(
        deployer_id="acme-eu",
        model_ref=build_model_ref_from_coordinate(
            "black-forest-labs/flux-schnell:bf2f2e683d03a9549f484a37a0df1c4c08e8e3fa3a18f3e1c1d4a4dba8c0bc0e",
            prediction_id="pred_001",
            status="succeeded",
        ),
        schema="synthetic_image/v1",
        prompt_text="a serene mountain lake",
        inputs={"prompt": "a serene mountain lake", "guidance_scale": 7.5},
        output_bytes=image,
        output_media_type="image/png",
        signer=signer,
        emitter=QueueEmitter(captured.append),
    )

    assert len(captured) == 1
    assert captured[0] is signed
    assert signed["signature_alg"] == "ed25519"
    receipt = signed["receipt"]
    assert receipt["schema"] == "synthetic_image/v1"
    assert receipt["model"]["model_id"] == "black-forest-labs/flux-schnell"
    assert receipt["model"]["model_version"].startswith("bf2f2e")
    assert receipt["output_artifacts"][0]["media_type"] == "image/png"
    # Input refs include the prompt and guidance_scale
    assert {r["name"] for r in receipt["input_refs"]} == {"prompt", "guidance_scale"}

    # C4: offline verification
    canonical = canonical_encode(receipt)
    sig = base64.b64decode(signed["signature_b64"])
    assert verify(signer.public_key_bytes(), canonical, sig)


def test_emit_receipt_requires_model_ref_or_prediction():
    import pytest

    with pytest.raises(ValueError):
        emit_receipt(deployer_id="acme-eu")
