"""Async wrapper tests."""

import pytest


def _capture_sink():
    from ledgerproof_groq.emitter import ReceiptSink
    captured = []

    class Cap(ReceiptSink):
        def write(self, r):
            captured.append(r)

    return Cap(), captured


@pytest.mark.asyncio
async def test_async_chat_completion_emits_receipt():
    from ledgerproof_groq import LedgerProofAsyncGroq
    sink, captured = _capture_sink()
    client = LedgerProofAsyncGroq(
        api_key="test",
        lpr_deployer_id="d-async",
        lpr_sink=sink,
    )
    resp = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "hi"}],
    )
    assert resp.choices[0].message.content == "Hello there."
    client.flush()
    assert len(captured) == 1


@pytest.mark.asyncio
async def test_async_audio_transcription():
    import io
    from ledgerproof_groq import LedgerProofAsyncGroq
    sink, captured = _capture_sink()
    client = LedgerProofAsyncGroq(
        api_key="test",
        lpr_deployer_id="d-async",
        lpr_sink=sink,
    )
    await client.audio.transcriptions.create(
        file=io.BytesIO(b"abc"),
        model="whisper-large-v3",
        lpr_schema="audio_transcription/v1",
    )
    client.flush()
    assert len(captured) == 1
