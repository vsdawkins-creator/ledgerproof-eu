"""End-to-end model_wrapper behaviour against a mocked watsonx.ai ModelInference."""

from __future__ import annotations

import base64

from ledgerproof_watsonx import (
    Ed25519Signer,
    LedgerProofModelInference,
    QueueEmitter,
    make_model,
    verify,
)
from ledgerproof_watsonx.canonical import canonical_encode


class _FakeCredentials:
    def __init__(self, url: str):
        self.url = url


class _FakeModelInference:
    """Minimal stand-in for ibm_watsonx_ai.foundation_models.ModelInference."""

    def __init__(self, model_id: str, credentials, project_id: str | None = None):
        self.model_id = model_id
        self.credentials = credentials
        self.project_id = project_id
        self.chat_calls = []
        self.chat_stream_calls = []
        self.generate_calls = []
        self.generate_stream_calls = []

    def chat(self, messages, **kwargs):
        self.chat_calls.append({"messages": messages, **kwargs})
        return {
            "id": "chatcmpl-eu-1",
            "model": self.model_id,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "Hallo!"},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 3, "completion_tokens": 1},
        }

    def chat_stream(self, messages, **kwargs):
        self.chat_stream_calls.append({"messages": messages, **kwargs})
        events = [
            {"id": "chatcmpl-stream-1", "model": self.model_id,
             "choices": [{"index": 0, "delta": {"content": "Bon"}}]},
            {"choices": [{"index": 0, "delta": {"content": "jour"}}]},
            {"choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]},
        ]
        return iter(events)

    def generate_text(self, prompt=None, **kwargs):
        self.generate_calls.append({"prompt": prompt, **kwargs})
        return {
            "id": "gen-1",
            "model_id": self.model_id,
            "results": [{"generated_text": "Bonjour", "stop_reason": "eos_token"}],
        }

    def generate_text_stream(self, prompt=None, **kwargs):
        self.generate_stream_calls.append({"prompt": prompt, **kwargs})
        return iter(["Hal", "lo"])


def _make_wrapper(**extra):
    captured = []
    creds = _FakeCredentials("https://eu-de.ml.cloud.ibm.com")
    inner = _FakeModelInference(
        model_id="ibm/granite-3-8b-instruct",
        credentials=creds,
        project_id="11111111-2222-3333-4444-555555555555",
    )
    signer = Ed25519Signer()
    wrapper = LedgerProofModelInference(
        deployer_id="acme-eu",
        inner=inner,
        signer=signer,
        emitter=QueueEmitter(captured.append),
        **extra,
    )
    return wrapper, inner, captured, signer


def test_chat_emits_signed_receipt_and_response_unchanged():
    wrapper, inner, captured, signer = _make_wrapper()
    resp = wrapper.chat(messages=[{"role": "user", "content": "Hallo!"}])

    # Response is unchanged.
    assert resp["choices"][0]["message"]["content"] == "Hallo!"

    assert len(captured) == 1
    signed = captured[0]
    receipt = signed["receipt"]
    assert receipt["schema"] == "chatbot_session/v1"
    assert receipt["model"]["upstream_provider"] == "ibm"
    assert receipt["model"]["region"] == "eu-de"
    assert receipt["model"]["project_id"] == "11111111-2222-3333-4444-555555555555"
    assert receipt["model"]["is_open_weights"] is True
    assert receipt["streaming"] is False
    assert len(receipt["content_refs"]) == 2

    # Signature verifies offline (C4).
    sig = base64.b64decode(signed["signature_b64"])
    assert verify(signer.public_key_bytes(), canonical_encode(receipt), sig)


def test_chat_region_pulled_from_credentials_url():
    captured = []
    creds = _FakeCredentials("https://us-south.ml.cloud.ibm.com")
    inner = _FakeModelInference(
        model_id="meta-llama/llama-3-1-70b-instruct",
        credentials=creds,
    )
    wrapper = LedgerProofModelInference(
        deployer_id="acme",
        inner=inner,
        emitter=QueueEmitter(captured.append),
    )
    wrapper.chat(messages=[{"role": "user", "content": "hi"}])
    r = captured[0]["receipt"]
    assert r["model"]["region"] == "us-south"
    assert r["model"]["upstream_provider"] == "meta"
    assert r["model"]["is_open_weights"] is False


def test_residency_schema_when_attest_residency_true():
    wrapper, _, captured, _ = _make_wrapper(
        attest_residency=True,
        sccs_in_place=True,
        tenant_id="acme-de-hash",
    )
    wrapper.chat(messages=[{"role": "user", "content": "hi"}])
    r = captured[-1]["receipt"]
    assert r["schema"] == "eu_data_residency/v1"
    assert r["residency"]["eu_region"] is True
    assert r["residency"]["sccs_in_place"] is True
    assert r["residency"]["tenant_id"] == "acme-de-hash"
    assert r["residency"]["attested_region"] == "eu-de"


def test_granite_schema_when_attest_granite_open_weights_true():
    wrapper, _, captured, _ = _make_wrapper(attest_granite_open_weights=True)
    wrapper.chat(messages=[{"role": "user", "content": "hi"}])
    r = captured[-1]["receipt"]
    assert r["schema"] == "granite_open_model/v1"
    assert r["open_weights"]["license_spdx"] == "Apache-2.0"
    assert r["open_weights"]["model_family"] == "ibm-granite"


def test_residency_and_granite_combined_residency_wins_schema():
    wrapper, _, captured, _ = _make_wrapper(
        attest_residency=True,
        attest_granite_open_weights=True,
    )
    wrapper.chat(messages=[{"role": "user", "content": "hi"}])
    r = captured[-1]["receipt"]
    # Residency schema wins; open_weights rides as side-field.
    assert r["schema"] == "eu_data_residency/v1"
    assert r["open_weights"]["license_spdx"] == "Apache-2.0"
    assert r["residency"]["eu_region"] is True


def test_chat_stream_emits_one_receipt_after_iteration():
    wrapper, _, captured, _ = _make_wrapper()
    stream = wrapper.chat_stream(messages=[{"role": "user", "content": "stream me"}])
    events = list(stream)
    assert len(events) == 3
    assert len(captured) == 1
    r = captured[0]["receipt"]
    assert r["streaming"] is True
    assistant_ref = [c for c in r["content_refs"] if c["role"] == "assistant"][0]
    assert assistant_ref["byte_length"] == len("Bonjour".encode("utf-8"))


def test_generate_text_emits_receipt():
    wrapper, _, captured, _ = _make_wrapper()
    resp = wrapper.generate_text(prompt="Bonjour")
    assert resp["results"][0]["generated_text"] == "Bonjour"
    r = captured[-1]["receipt"]
    assert r["streaming"] is False
    assistant_ref = [c for c in r["content_refs"] if c["role"] == "assistant"][0]
    assert assistant_ref["byte_length"] == len("Bonjour".encode("utf-8"))


def test_generate_text_stream_emits_one_receipt():
    wrapper, _, captured, _ = _make_wrapper()
    stream = wrapper.generate_text_stream(prompt="hi")
    events = list(stream)
    assert events == ["Hal", "lo"]
    r = captured[-1]["receipt"]
    assert r["streaming"] is True
    assistant_ref = [c for c in r["content_refs"] if c["role"] == "assistant"][0]
    assert assistant_ref["byte_length"] == len("Hallo".encode("utf-8"))


def test_make_model_factory():
    creds = _FakeCredentials("https://eu-de.ml.cloud.ibm.com")
    inner = _FakeModelInference(
        model_id="ibm/granite-3-8b-instruct", credentials=creds
    )
    captured = []
    m = make_model(
        deployer_id="acme",
        inner=inner,
        emitter=QueueEmitter(captured.append),
    )
    m.chat(messages=[{"role": "user", "content": "hi"}])
    assert captured[-1]["receipt"]["model"]["upstream_provider"] == "ibm"


def test_attribute_fall_through_to_inner():
    wrapper, inner, _, _ = _make_wrapper()
    # `model_id` exists on inner; should be reachable via wrapper attribute access.
    assert wrapper.model_id == "ibm/granite-3-8b-instruct"
