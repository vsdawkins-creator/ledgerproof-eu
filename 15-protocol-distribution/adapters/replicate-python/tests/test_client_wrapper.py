"""
Client wrapper tests using mocked Replicate clients (no network).

We mock the inner `replicate.Client` so the tests run on a fresh venv without
a Replicate API token.
"""

from __future__ import annotations

import base64
from types import SimpleNamespace
from unittest.mock import MagicMock

from ledgerproof_replicate import (
    LedgerProofReplicateClient,
    QueueEmitter,
)
from ledgerproof_replicate.canonical import canonical_encode
from ledgerproof_replicate.signer import Ed25519Signer, verify


def _make_wrapper(emitter_sink, output, schema=None):
    fake_inner = MagicMock()
    fake_inner.run.return_value = output
    return LedgerProofReplicateClient(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(emitter_sink.append),
        signer=Ed25519Signer(),
        schema=schema,
    ), fake_inner


def test_sync_run_text_output_emits_chatbot_session_receipt():
    captured: list = []
    wrapper, fake = _make_wrapper(captured, output="Hello, world.")

    output = wrapper.run(
        "meta/meta-llama-3-70b-instruct",
        input={"prompt": "Say hi"},
    )
    assert output == "Hello, world."  # C7: unchanged

    assert len(captured) == 1
    signed = captured[0]
    assert signed["signature_alg"] == "ed25519"
    assert signed["receipt"]["deployer_id"] == "acme-eu-test"
    assert signed["receipt"]["schema"] == "chatbot_session/v1"
    assert signed["receipt"]["model"]["provider"] == "replicate"
    assert signed["receipt"]["model"]["model_id"] == "meta/meta-llama-3-70b-instruct"
    assert signed["receipt"]["streaming"] is False


def test_sync_run_image_url_output_emits_synthetic_image_receipt():
    captured: list = []
    image_url = "https://replicate.delivery/pbxt/abc/out.png"
    wrapper, _ = _make_wrapper(captured, output=[image_url])

    wrapper.run(
        "black-forest-labs/flux-schnell:bf2f2e683d03a9549f484a37a0df1c4c08e8e3fa3a18f3e1c1d4a4dba8c0bc0e",
        input={"prompt": "a serene mountain lake"},
    )

    signed = captured[0]
    assert signed["receipt"]["schema"] == "synthetic_image/v1"
    assert signed["receipt"]["model"]["model_version"].startswith("bf2f2e")
    artifacts = signed["receipt"]["output_artifacts"]
    assert len(artifacts) == 1
    assert artifacts[0]["media_type"] == "image/png"
    # prompt was hashed into input_refs and into content_refs
    assert any(r["name"] == "prompt" for r in signed["receipt"]["input_refs"])


def test_sync_run_audio_url_output_emits_synthetic_audio_receipt():
    captured: list = []
    audio_url = "https://replicate.delivery/pbxt/abc/out.wav"
    wrapper, _ = _make_wrapper(captured, output=audio_url)

    wrapper.run(
        "meta/musicgen",
        input={"prompt": "ambient piano", "duration": 30},
    )

    signed = captured[0]
    assert signed["receipt"]["schema"] == "synthetic_audio/v1"
    assert signed["receipt"]["output_artifacts"][0]["media_type"] == "audio/wav"


def test_sync_run_video_url_output_emits_synthetic_video_receipt():
    captured: list = []
    video_url = "https://replicate.delivery/pbxt/abc/out.mp4"
    wrapper, _ = _make_wrapper(captured, output=[video_url])

    wrapper.run(
        "anotherjesse/zeroscope-v2-xl",
        input={"prompt": "a fox jumping"},
    )

    signed = captured[0]
    assert signed["receipt"]["schema"] == "synthetic_video/v1"
    assert signed["receipt"]["output_artifacts"][0]["media_type"] == "video/mp4"


def test_run_image_forces_schema_even_for_text_output():
    captured: list = []
    wrapper, _ = _make_wrapper(captured, output="some text that would normally be chatbot")

    wrapper.run_image(
        "black-forest-labs/flux-schnell",
        input={"prompt": "test"},
    )
    assert captured[0]["receipt"]["schema"] == "synthetic_image/v1"


def test_run_with_attribution_requires_version():
    import pytest

    wrapper, _ = _make_wrapper([], output="x")
    with pytest.raises(ValueError):
        wrapper.run_with_attribution(
            "black-forest-labs/flux-schnell",  # no :version
            input={"prompt": "x"},
        )


def test_run_with_attribution_emits_multimodel_attribution():
    captured: list = []
    wrapper, _ = _make_wrapper(
        captured,
        output=["https://replicate.delivery/pbxt/abc/out.png"],
    )
    wrapper.run_with_attribution(
        "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
        input={"prompt": "modernist EU parliament"},
    )
    signed = captured[0]
    assert signed["receipt"]["schema"] == "multimodel_attribution/v1"
    assert signed["receipt"]["model"]["model_version"].startswith("39ed52f2")


def test_streaming_emits_incremental_hash_receipt():
    captured: list = []

    def fake_stream(ref, input=None, **kwargs):
        for delta in ["Hel", "lo, ", "world."]:
            yield SimpleNamespace(event="output", data=delta)
        yield SimpleNamespace(event="done", data="")

    fake_inner = MagicMock()
    fake_inner.stream = fake_stream

    wrapper = LedgerProofReplicateClient(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )

    collected = []
    for ev in wrapper.stream(
        "meta/meta-llama-3-70b-instruct",
        input={"prompt": "Hi"},
    ):
        if ev.event == "output":
            collected.append(ev.data)
    assert "".join(collected) == "Hello, world."

    assert len(captured) == 1
    signed = captured[0]
    assert signed["receipt"]["streaming"] is True
    output_ref = next(c for c in signed["receipt"]["content_refs"] if c["role"] == "output")
    assert output_ref["byte_length"] == len("Hello, world.".encode("utf-8"))


def test_signature_verifies_with_published_public_key():
    """C4: offline verification works given the public key bytes."""
    captured: list = []
    signer = Ed25519Signer()
    fake_inner = MagicMock()
    fake_inner.run.return_value = "result text"

    wrapper = LedgerProofReplicateClient(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=signer,
    )
    wrapper.run("meta/meta-llama-3-70b-instruct", input={"prompt": "verify me"})

    signed = captured[0]
    canonical = canonical_encode(signed["receipt"])
    sig = base64.b64decode(signed["signature_b64"])
    assert verify(signer.public_key_bytes(), canonical, sig)


def test_response_is_not_mutated_by_adapter():
    """C7: the response object is returned as-is."""
    captured: list = []
    pre_output = ["https://replicate.delivery/pbxt/abc/out.png"]
    fake_inner = MagicMock()
    fake_inner.run.return_value = pre_output

    wrapper = LedgerProofReplicateClient(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )
    post = wrapper.run("black-forest-labs/flux-schnell", input={"prompt": "ping"})
    assert post is pre_output
    assert not hasattr(post, "ledgerproof_receipt")


def test_passthrough_to_inner_client_for_unknown_attr():
    """The wrapper forwards unknown attribute access (e.g. predictions)."""
    fake_inner = MagicMock()
    fake_inner.predictions = "PREDICTIONS_NAMESPACE"
    wrapper = LedgerProofReplicateClient(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter([].append),
        signer=Ed25519Signer(),
    )
    assert wrapper.predictions == "PREDICTIONS_NAMESPACE"
