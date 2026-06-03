"""Async wrapper tests."""

import pytest


def _capture_sink():
    from ledgerproof_cerebras.emitter import ReceiptSink
    captured = []

    class Cap(ReceiptSink):
        def write(self, r):
            captured.append(r)

    return Cap(), captured


@pytest.mark.asyncio
async def test_async_chat_completion_emits_receipt():
    from ledgerproof_cerebras import LedgerProofAsyncCerebras
    sink, captured = _capture_sink()
    client = LedgerProofAsyncCerebras(
        api_key="test",
        lpr_deployer_id="d-async",
        lpr_sink=sink,
    )
    resp = await client.chat.completions.create(
        model="llama3.1-70b",
        messages=[{"role": "user", "content": "hi"}],
    )
    assert resp.choices[0].message.content == "Hello there."
    client.flush()
    assert len(captured) == 1


@pytest.mark.asyncio
async def test_async_reasoning_model_routes_to_reasoning_schema():
    from ledgerproof_cerebras import LedgerProofAsyncCerebras
    from ledgerproof_cerebras.canonical import canonical_decode
    sink, captured = _capture_sink()
    client = LedgerProofAsyncCerebras(
        api_key="test",
        lpr_deployer_id="d-async",
        lpr_sink=sink,
    )
    await client.chat.completions.create(
        model="qwen3-32b-thinking",
        messages=[{"role": "user", "content": "Solve."}],
    )
    client.flush()
    decoded = canonical_decode(captured[0].payload_cbor)
    assert decoded["payload"]["schema_name"] == "reasoning_distilled/v1"


@pytest.mark.asyncio
async def test_async_wafer_scale_schema():
    from ledgerproof_cerebras import LedgerProofAsyncCerebras
    from ledgerproof_cerebras.canonical import canonical_decode
    sink, captured = _capture_sink()
    client = LedgerProofAsyncCerebras(
        api_key="test",
        lpr_deployer_id="d-async",
        lpr_sink=sink,
    )
    await client.chat.completions.create(
        model="llama3.1-70b",
        messages=[{"role": "user", "content": "hi"}],
        lpr_schema="wafer_scale_inference/v1",
    )
    client.flush()
    payload = canonical_decode(captured[0].payload_cbor)["payload"]
    assert payload["schema_name"] == "wafer_scale_inference/v1"
    assert payload["hardware_class"] == "wafer-scale"
