"""
Model wrapper tests using a mocked GenerativeModel (no network).

We inject a MagicMock as the inner model so tests run on a fresh venv with no
GOOGLE_API_KEY.
"""

from __future__ import annotations

import base64
from types import SimpleNamespace
from unittest.mock import MagicMock

from ledgerproof_google_ai import (
    LedgerProofGenerativeModel,
    QueueEmitter,
)
from ledgerproof_google_ai.canonical import canonical_encode
from ledgerproof_google_ai.signer import Ed25519Signer, verify


def _fake_text_response(text="Hello, Gemini.", with_function_call=False):
    text_part = SimpleNamespace(text=text, function_call=None)
    parts = [text_part]
    if with_function_call:
        fc = SimpleNamespace(name="lookup_weather", args={"city": "Berlin"})
        parts.append(SimpleNamespace(text=None, function_call=fc))
    candidate = SimpleNamespace(
        content=SimpleNamespace(parts=parts, role="model"),
        finish_reason="STOP",
    )
    usage = SimpleNamespace(
        prompt_token_count=7,
        candidates_token_count=4,
        total_token_count=11,
    )
    return SimpleNamespace(
        text=text,
        candidates=[candidate],
        usage_metadata=usage,
        response_id="resp_abc_001",
        model_version="gemini-2.0-flash",
    )


def _make_wrapper(captured, *, with_function_call=False):
    fake_inner = MagicMock()
    fake_inner.generate_content.return_value = _fake_text_response(
        with_function_call=with_function_call
    )
    return LedgerProofGenerativeModel(
        fake_inner,
        deployer_id="acme-eu-test",
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )


def test_generate_content_emits_receipt_and_returns_response_unchanged():
    captured: list = []
    wrapper = _make_wrapper(captured)
    response = wrapper.generate_content("Hi there")

    # C7: response passed through unchanged.
    assert response.text == "Hello, Gemini."
    assert response.response_id == "resp_abc_001"

    assert len(captured) == 1
    signed = captured[0]
    assert signed["signature_alg"] == "ed25519"
    receipt = signed["receipt"]
    assert receipt["deployer_id"] == "acme-eu-test"
    assert receipt["schema"] == "chatbot_session/v1"
    assert receipt["streaming"] is False
    roles = [c["role"] for c in receipt["content_refs"]]
    assert "user" in roles and "model" in roles
    # Token counts copied through:
    assert receipt["model"]["total_token_count"] == 11


def test_generate_content_with_function_call_promotes_schema():
    captured: list = []
    wrapper = _make_wrapper(captured, with_function_call=True)
    wrapper.generate_content("What's the weather in Berlin?")
    receipt = captured[0]["receipt"]
    assert receipt["schema"] == "gemini_function_call/v1"
    assert receipt["function_calls"][0]["function_name"] == "lookup_weather"
    assert len(receipt["function_calls"][0]["args_sha256_hex"]) == 64


def test_streaming_generate_content_emits_with_incremental_hash():
    captured: list = []

    chunks = [
        SimpleNamespace(text="Hel", function_call=None, candidates=[]),
        SimpleNamespace(text="lo, ", function_call=None, candidates=[]),
        SimpleNamespace(text="Gemini.", function_call=None, candidates=[]),
    ]

    fake_inner = MagicMock()
    # When stream=True the SDK returns an iterable.
    fake_inner.generate_content.return_value = iter(chunks)

    wrapper = LedgerProofGenerativeModel(
        fake_inner,
        deployer_id="acme-eu-test",
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )
    stream = wrapper.generate_content("Hi", stream=True)
    collected = "".join(c.text for c in stream)
    assert collected == "Hello, Gemini."

    assert len(captured) == 1
    receipt = captured[0]["receipt"]
    assert receipt["streaming"] is True
    asst = next(c for c in receipt["content_refs"] if c["role"] == "model")
    assert asst["byte_length"] == len("Hello, Gemini.".encode("utf-8"))


def test_multimodal_input_promotes_schema():
    captured: list = []
    fake_inner = MagicMock()
    fake_inner.generate_content.return_value = _fake_text_response(
        text="An orange tabby cat."
    )
    wrapper = LedgerProofGenerativeModel(
        fake_inner,
        deployer_id="acme-eu-test",
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )
    # Simulate the dict-form of an inline image part used by google-generativeai.
    image_part = {"inline_data": {"mime_type": "image/png", "data": b"\x89PNG..."}}
    wrapper.generate_content(["Describe this image:", image_part])
    receipt = captured[0]["receipt"]
    assert receipt["schema"] == "multimodal_generation/v1"
    assert "image" in receipt["input_modalities"]


def test_signature_verifies_offline_with_public_key():
    """C4: offline verification works given the public key bytes."""
    captured: list = []
    signer = Ed25519Signer()
    fake_inner = MagicMock()
    fake_inner.generate_content.return_value = _fake_text_response()
    wrapper = LedgerProofGenerativeModel(
        fake_inner,
        deployer_id="acme-eu-test",
        emitter=QueueEmitter(captured.append),
        signer=signer,
    )
    wrapper.generate_content("Verify me")
    signed = captured[0]
    canonical_bytes = canonical_encode(signed["receipt"])
    sig = base64.b64decode(signed["signature_b64"])
    assert verify(signer.public_key_bytes(), canonical_bytes, sig)


def test_unknown_attributes_forwarded_to_inner_model():
    fake_inner = MagicMock()
    fake_inner.count_tokens.return_value = SimpleNamespace(total_tokens=42)
    wrapper = LedgerProofGenerativeModel(
        fake_inner,
        deployer_id="acme-eu-test",
        emitter=QueueEmitter(lambda _: None),
        signer=Ed25519Signer(),
    )
    result = wrapper.count_tokens("how many tokens")
    assert result.total_tokens == 42
