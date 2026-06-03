"""Wrapper tests using a fake Cerebras Cloud SDK (see conftest.py)."""

from typing import List


def _capture_sink():
    from ledgerproof_cerebras.emitter import ReceiptSink
    captured: List = []

    class Cap(ReceiptSink):
        def write(self, r):
            captured.append(r)

    return Cap(), captured


def test_chat_completion_emits_receipt():
    from ledgerproof_cerebras import LedgerProofCerebras
    sink, captured = _capture_sink()
    client = LedgerProofCerebras(
        api_key="test",
        lpr_deployer_id="d-test",
        lpr_sink=sink,
    )
    resp = client.chat.completions.create(
        model="llama3.1-70b",
        messages=[{"role": "user", "content": "hi"}],
    )
    assert resp.choices[0].message.content == "Hello there."
    client.flush()
    assert len(captured) == 1
    assert captured[0].signature is not None


def test_chat_completion_wafer_scale_schema():
    from ledgerproof_cerebras import LedgerProofCerebras
    from ledgerproof_cerebras.canonical import canonical_decode

    sink, captured = _capture_sink()
    client = LedgerProofCerebras(
        api_key="test",
        lpr_deployer_id="d-test",
        lpr_sink=sink,
    )
    client.chat.completions.create(
        model="llama3.1-70b",
        messages=[{"role": "user", "content": "hi"}],
        lpr_schema="wafer_scale_inference/v1",
    )
    client.flush()
    decoded = canonical_decode(captured[0].payload_cbor)
    payload = decoded["payload"]
    assert payload["schema_name"] == "wafer_scale_inference/v1"
    assert "inference_latency_ms" in payload
    assert payload["prompt_tokens"] == 5
    assert payload["completion_tokens"] == 3
    assert payload["hardware_class"] == "wafer-scale"
    assert decoded["adapter"] == "ledgerproof-cerebras"


def test_reasoning_model_auto_routes_to_reasoning_schema():
    """Without an explicit schema, a deepseek-r1 model should land on the
    reasoning_distilled schema."""
    from ledgerproof_cerebras import LedgerProofCerebras
    from ledgerproof_cerebras.canonical import canonical_decode

    sink, captured = _capture_sink()
    client = LedgerProofCerebras(
        api_key="test",
        lpr_deployer_id="d-test",
        lpr_sink=sink,
    )
    client.chat.completions.create(
        model="deepseek-r1-distill-llama-70b",
        messages=[{"role": "user", "content": "Why is the sky blue?"}],
    )
    client.flush()
    decoded = canonical_decode(captured[0].payload_cbor)
    payload = decoded["payload"]
    assert payload["schema_name"] == "reasoning_distilled/v1"
    assert payload["reasoning_tokens"] == 42
    assert payload["completion_tokens"] == 8


def test_streaming_emits_one_receipt_after_consumption():
    from ledgerproof_cerebras import LedgerProofCerebras
    sink, captured = _capture_sink()
    client = LedgerProofCerebras(
        api_key="test",
        lpr_deployer_id="d-test",
        lpr_sink=sink,
    )
    stream = client.chat.completions.create(
        model="llama3.1-70b",
        messages=[{"role": "user", "content": "hi"}],
        stream=True,
    )
    assert len(captured) == 0  # nothing yet
    pieces = [ev.choices[0].delta.content for ev in stream]
    assert "".join(pieces) == "Hello there."
    client.flush()
    assert len(captured) == 1


def test_skip_does_not_emit():
    from ledgerproof_cerebras import LedgerProofCerebras
    sink, captured = _capture_sink()
    client = LedgerProofCerebras(
        api_key="test",
        lpr_deployer_id="d-test",
        lpr_sink=sink,
    )
    client.chat.completions.create(
        model="llama3.1-70b",
        messages=[{"role": "user", "content": "hi"}],
        lpr_skip=True,
    )
    client.flush()
    assert len(captured) == 0


def test_receipt_signature_locally_verifiable():
    from ledgerproof_cerebras import LedgerProofCerebras
    from ledgerproof_cerebras.signer import verify_signature
    sink, captured = _capture_sink()
    client = LedgerProofCerebras(
        api_key="test",
        lpr_deployer_id="d-test",
        lpr_sink=sink,
    )
    client.chat.completions.create(
        model="llama3.1-70b",
        messages=[{"role": "user", "content": "hi"}],
    )
    client.flush()
    r = captured[0]
    assert verify_signature(r.public_key_b64, r.signature, r.payload_cbor)


def test_generated_content_schema_explicit():
    from ledgerproof_cerebras import LedgerProofCerebras
    from ledgerproof_cerebras.canonical import canonical_decode
    sink, captured = _capture_sink()
    client = LedgerProofCerebras(
        api_key="test",
        lpr_deployer_id="d-test",
        lpr_sink=sink,
    )
    client.chat.completions.create(
        model="llama3.1-8b",
        messages=[{"role": "user", "content": "hi"}],
        lpr_schema="generated_content/v1",
        lpr_marking_method="visible-label",
    )
    client.flush()
    payload = canonical_decode(captured[0].payload_cbor)["payload"]
    assert payload["schema_name"] == "generated_content/v1"
    assert payload["marking_method"] == "visible-label"
