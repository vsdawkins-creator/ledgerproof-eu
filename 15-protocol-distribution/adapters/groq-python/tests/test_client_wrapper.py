"""Wrapper tests using a fake Groq SDK (see conftest.py)."""

from typing import List


def _capture_sink():
    from ledgerproof_groq.emitter import ReceiptSink
    captured: List = []

    class Cap(ReceiptSink):
        def write(self, r):
            captured.append(r)

    return Cap(), captured


def test_chat_completion_emits_receipt():
    from ledgerproof_groq import LedgerProofGroq
    sink, captured = _capture_sink()
    client = LedgerProofGroq(
        api_key="test",
        lpr_deployer_id="d-test",
        lpr_sink=sink,
    )
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "hi"}],
    )
    assert resp.choices[0].message.content == "Hello there."
    client.flush()
    assert len(captured) == 1
    assert captured[0].signature is not None


def test_chat_completion_low_latency_schema():
    from ledgerproof_groq import LedgerProofGroq
    from ledgerproof_groq.canonical import canonical_decode

    sink, captured = _capture_sink()
    client = LedgerProofGroq(
        api_key="test",
        lpr_deployer_id="d-test",
        lpr_sink=sink,
    )
    client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "hi"}],
        lpr_schema="low_latency_inference/v1",
    )
    client.flush()
    decoded = canonical_decode(captured[0].payload_cbor)
    payload = decoded["payload"]
    assert payload["schema_name"] == "low_latency_inference/v1"
    assert "inference_latency_ms" in payload
    assert payload["prompt_tokens"] == 5
    assert payload["completion_tokens"] == 3


def test_streaming_emits_one_receipt_after_consumption():
    from ledgerproof_groq import LedgerProofGroq
    sink, captured = _capture_sink()
    client = LedgerProofGroq(
        api_key="test",
        lpr_deployer_id="d-test",
        lpr_sink=sink,
    )
    stream = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "hi"}],
        stream=True,
    )
    assert len(captured) == 0  # nothing yet
    pieces = [ev.choices[0].delta.content for ev in stream]
    assert "".join(pieces) == "Hello there."
    client.flush()
    assert len(captured) == 1


def test_audio_transcription_emits_receipt():
    import io
    from ledgerproof_groq import LedgerProofGroq
    from ledgerproof_groq.canonical import canonical_decode

    sink, captured = _capture_sink()
    client = LedgerProofGroq(
        api_key="test",
        lpr_deployer_id="d-test",
        lpr_sink=sink,
    )
    f = io.BytesIO(b"\x00\x01\x02fake audio")
    client.audio.transcriptions.create(
        file=f, model="whisper-large-v3",
        lpr_schema="audio_transcription/v1",
    )
    client.flush()
    decoded = canonical_decode(captured[0].payload_cbor)
    assert decoded["payload"]["schema_name"] == "audio_transcription/v1"
    assert decoded["payload"]["audio_hash"].startswith("sha256:")


def test_skip_does_not_emit():
    from ledgerproof_groq import LedgerProofGroq
    sink, captured = _capture_sink()
    client = LedgerProofGroq(
        api_key="test",
        lpr_deployer_id="d-test",
        lpr_sink=sink,
    )
    client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "hi"}],
        lpr_skip=True,
    )
    client.flush()
    assert len(captured) == 0


def test_receipt_signature_locally_verifiable():
    from ledgerproof_groq import LedgerProofGroq
    from ledgerproof_groq.signer import verify_signature
    sink, captured = _capture_sink()
    client = LedgerProofGroq(
        api_key="test",
        lpr_deployer_id="d-test",
        lpr_sink=sink,
    )
    client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "hi"}],
    )
    client.flush()
    r = captured[0]
    assert verify_signature(r.public_key_b64, r.signature, r.payload_cbor)
