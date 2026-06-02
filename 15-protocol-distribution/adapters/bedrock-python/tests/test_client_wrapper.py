"""End-to-end client wrapper behaviour against a mocked boto3 bedrock-runtime client."""

from __future__ import annotations

import io
import json

from ledgerproof_bedrock import (
    Ed25519Signer,
    LedgerProofBedrockClient,
    QueueEmitter,
    install_converse_methods,
    make_client,
    verify,
)
from ledgerproof_bedrock.canonical import canonical_encode


class _FakeStreamingBody:
    def __init__(self, data: bytes):
        self._buf = io.BytesIO(data)

    def read(self):
        return self._buf.read()


class _FakeBedrockClient:
    """Minimal stand-in for boto3.client('bedrock-runtime')."""

    class _Meta:
        region_name = "eu-west-1"

    meta = _Meta()

    def __init__(self):
        self.invoke_calls = []
        self.converse_calls = []
        self.stream_calls = []

    # ---------- invoke_model ----------
    def invoke_model(self, **kwargs):
        self.invoke_calls.append(kwargs)
        body = {
            "id": "msg_01ABC",
            "content": [{"type": "text", "text": "Hallo!"}],
            "stop_reason": "end_turn",
            "usage": {"input_tokens": 5, "output_tokens": 2},
        }
        return {
            "body": _FakeStreamingBody(json.dumps(body).encode("utf-8")),
            "contentType": "application/json",
            "ResponseMetadata": {"RequestId": "req-123"},
        }

    # ---------- converse ----------
    def converse(self, **kwargs):
        self.converse_calls.append(kwargs)
        return {
            "output": {
                "message": {
                    "role": "assistant",
                    "content": [{"text": "Bonjour"}],
                }
            },
            "stopReason": "end_turn",
            "usage": {"inputTokens": 4, "outputTokens": 1},
            "ResponseMetadata": {"RequestId": "req-456"},
        }

    # ---------- streaming ----------
    def invoke_model_with_response_stream(self, **kwargs):
        self.stream_calls.append(kwargs)
        events = [
            {"chunk": {"bytes": json.dumps(
                {"type": "content_block_delta", "delta": {"text": "Hel"}}
            ).encode("utf-8")}},
            {"chunk": {"bytes": json.dumps(
                {"type": "content_block_delta", "delta": {"text": "lo"}}
            ).encode("utf-8")}},
            {"chunk": {"bytes": json.dumps(
                {"type": "message_stop", "amazon-bedrock-invocationMetrics": {"inputTokenCount": 3}}
            ).encode("utf-8")}},
        ]
        return {"body": iter(events)}

    def converse_stream(self, **kwargs):
        events = [
            {"contentBlockDelta": {"delta": {"text": "Bon"}, "contentBlockIndex": 0}},
            {"contentBlockDelta": {"delta": {"text": "jour"}, "contentBlockIndex": 0}},
            {"messageStop": {"stopReason": "end_turn"}},
            {"metadata": {"usage": {"inputTokens": 2, "outputTokens": 1}}},
        ]
        return {"stream": iter(events)}


def _make_client_with_capture(**extra):
    captured = []
    raw = _FakeBedrockClient()
    signer = Ed25519Signer()
    client = LedgerProofBedrockClient(
        deployer_id="acme-eu",
        client=raw,
        signer=signer,
        emitter=QueueEmitter(captured.append),
        **extra,
    )
    return client, raw, captured, signer


def test_invoke_model_emits_signed_receipt_and_response_body_remains_readable():
    client, raw, captured, signer = _make_client_with_capture()
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [{"role": "user", "content": "Hallo!"}],
        "max_tokens": 100,
    })
    resp = client.invoke_model(
        modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
        body=body,
    )

    # Caller can still read the response body — C7 / non-invasive.
    decoded = json.loads(resp["body"].read())
    assert decoded["content"][0]["text"] == "Hallo!"

    assert len(captured) == 1
    signed = captured[0]
    receipt = signed["receipt"]
    assert receipt["schema"] == "chatbot_session/v1"
    assert receipt["model"]["upstream_provider"] == "anthropic"
    assert receipt["model"]["region"] == "eu-west-1"
    assert receipt["streaming"] is False
    # Two content refs: user + assistant.
    assert len(receipt["content_refs"]) == 2

    # Signature verifies against the bundled public key (C4).
    import base64

    sig = base64.b64decode(signed["signature_b64"])
    canon = canonical_encode(receipt)
    assert verify(signer.public_key_bytes(), canon, sig) is True


def test_invoke_model_provider_attribution_for_meta():
    client, raw, captured, _ = _make_client_with_capture()
    client.invoke_model(
        modelId="meta.llama3-70b-instruct-v1:0",
        body=json.dumps({"prompt": "Hi", "max_gen_len": 10}),
    )
    assert captured[-1]["receipt"]["model"]["upstream_provider"] == "meta"


def test_residency_schema_when_attest_residency_true():
    client, _, captured, _ = _make_client_with_capture(attest_residency=True, sccs_in_place=True)
    client.invoke_model(
        modelId="anthropic.claude-3-haiku-20240307-v1:0",
        body=json.dumps({"messages": [{"role": "user", "content": "hi"}]}),
    )
    r = captured[-1]["receipt"]
    assert r["schema"] == "eu_aws_data_residency/v1"
    assert r["residency"]["eu_region"] is True
    assert r["residency"]["sccs_in_place"] is True


def test_invoke_model_stream_emits_one_receipt_after_iteration():
    client, _, captured, _ = _make_client_with_capture()
    body = json.dumps({"messages": [{"role": "user", "content": "Stream please"}]})
    resp = client.invoke_model_with_response_stream(
        modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
        body=body,
    )
    # Drain the stream.
    events = list(resp["body"])
    assert len(events) == 3
    assert len(captured) == 1
    r = captured[0]["receipt"]
    assert r["streaming"] is True
    # Assistant content_ref has non-zero byte length.
    assistant_ref = [c for c in r["content_refs"] if c["role"] == "assistant"][0]
    assert assistant_ref["byte_length"] > 0


def test_converse_via_make_client_emits_receipt():
    captured = []
    raw = _FakeBedrockClient()
    client = LedgerProofBedrockClient(
        deployer_id="acme-eu",
        client=raw,
        emitter=QueueEmitter(captured.append),
    )
    install_converse_methods(client)

    resp = client.converse(
        modelId="mistral.mistral-large-2402-v1:0",
        messages=[{"role": "user", "content": [{"text": "Bonjour"}]}],
    )
    assert resp["output"]["message"]["content"][0]["text"] == "Bonjour"
    r = captured[-1]["receipt"]
    assert r["model"]["upstream_provider"] == "mistral"


def test_make_client_factory_returns_wrapper_with_converse():
    raw = _FakeBedrockClient()
    captured = []
    client = make_client(
        deployer_id="acme-eu",
        client=raw,
        emitter=QueueEmitter(captured.append),
    )
    client.converse(
        modelId="amazon.titan-text-express-v1",
        messages=[{"role": "user", "content": [{"text": "Hi"}]}],
    )
    assert captured[-1]["receipt"]["model"]["upstream_provider"] == "amazon"


def test_converse_stream_emits_one_receipt_with_streaming_true():
    raw = _FakeBedrockClient()
    captured = []
    client = make_client(
        deployer_id="acme-eu",
        client=raw,
        emitter=QueueEmitter(captured.append),
    )
    resp = client.converse_stream(
        modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
        messages=[{"role": "user", "content": [{"text": "Stream"}]}],
    )
    events = list(resp["stream"])
    assert len(events) == 4
    r = captured[-1]["receipt"]
    assert r["streaming"] is True
    assistant_ref = [c for c in r["content_refs"] if c["role"] == "assistant"][0]
    assert assistant_ref["byte_length"] == len("Bonjour".encode("utf-8"))
