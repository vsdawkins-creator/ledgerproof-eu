"""Emitter, decorator, and manual.emit tests."""
from __future__ import annotations

import base64
import json
import os

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from ledgerproof_vertexai import configure, emit_manual, lpr_track
from ledgerproof_vertexai.canonical import canonicalize


def test_manual_emit_signature_verifies(configured):
    env = emit_manual(
        schema="eu_data_residency/v1",
        model="gemini-2.0-flash-001",
        project="acme-eu",
        location="europe-west4",
        input_text="prompt",
        output_text="answer",
    )
    pk = Ed25519PublicKey.from_public_bytes(
        base64.b64decode(env["signature"]["public_key"])
    )
    pk.verify(
        base64.b64decode(env["signature"]["value"]),
        canonicalize(env["payload"]),
    )


def test_file_sink_writes_jsonl(tmp_path):
    path = tmp_path / "receipts.jsonl"
    configure(deployer_id="urn:lpr:deployer:t", sink=str(path))
    emit_manual(
        schema="generated_content/v1",
        model="gemini-2.0-flash-001",
        project="p",
        location="europe-west4",
        input_text="x",
        output_text="y",
    )
    emit_manual(
        schema="generated_content/v1",
        model="gemini-2.0-flash-001",
        project="p",
        location="europe-west4",
        input_text="x2",
        output_text="y2",
    )
    assert path.exists()
    lines = path.read_text().strip().splitlines()
    assert len(lines) == 2
    for line in lines:
        env = json.loads(line)
        assert env["protocol"] == "lpr/0.1"


def test_lpr_track_decorator_emits(configured):
    class _Resp:
        text = "decorated-output"

    @lpr_track(
        schema="generated_content/v1",
        model="gemini-2.0-flash-001",
        project="p",
        location="europe-west9",
    )
    def call_vertex(prompt: str):
        return _Resp()

    result = call_vertex(prompt="Bonjour")
    assert result.text == "decorated-output"  # C7
    assert len(configured) == 1
    p = configured[0]["payload"]
    assert p["vertex"]["location"] == "europe-west9"
    assert p["vertex"]["region_of_inference_attestation"] == "EU/FR"


def test_emit_without_deployer_id_raises():
    # Reset: no configure() called.
    import pytest

    from ledgerproof_vertexai.emitter import emit_receipt

    with pytest.raises(RuntimeError):
        emit_receipt(
            "generated_content/v1",
            model="m",
            project="p",
            location="europe-west4",
            input_text="x",
            output_text="y",
        )


def test_unknown_location_passthrough(configured):
    emit_manual(
        schema="generated_content/v1",
        model="gemini-2.0-flash-001",
        project="p",
        location="moon-base-1",
        input_text="a",
        output_text="b",
    )
    p = configured[0]["payload"]
    # Unknown locations: attestation falls back to the raw label.
    assert p["vertex"]["region_of_inference_attestation"] == "moon-base-1"
