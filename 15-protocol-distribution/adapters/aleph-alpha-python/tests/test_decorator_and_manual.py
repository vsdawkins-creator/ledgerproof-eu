"""Decorator + manual emission tests."""

from __future__ import annotations

import pytest

from ledgerproof_aleph_alpha import (
    InMemoryEmitter,
    emit_receipt,
    lpr_track,
    verify_receipt,
)


def test_emit_receipt_generated_content():
    sink = InMemoryEmitter()
    receipt = emit_receipt(
        article="50(2)",
        schema="generated_content/v1",
        prompt_text="Was ist Artikel 50?",
        completion_text="Artikel 50 betrifft Transparenz.",
        model="luminous-base",
        model_version="2024-09",
        emitter=sink,
    )
    assert verify_receipt(receipt) is True
    assert receipt["payload"]["schema_name"] == "generated_content/v1"
    assert receipt["payload"]["article"] == "50(2)"
    assert sink.receipts[0] == receipt


def test_emit_receipt_chatbot_session_autohash():
    sink = InMemoryEmitter()
    r = emit_receipt(
        article="50(1)",
        schema="chatbot_session/v1",
        prompt_text="hallo",
        completion_text="hallo zurück",
        model="luminous-base",
        emitter=sink,
    )
    assert r["payload"]["session_id_hash"] == r["payload"]["prompt_sha256"]


def test_emit_receipt_on_prem_sovereign_deployment():
    sink = InMemoryEmitter()
    r = emit_receipt(
        article="50(1)",
        schema="on_prem_sovereign_deployment/v1",
        prompt_text="confidential prompt",
        completion_text="confidential completion",
        model="luminous-supreme-control",
        extra={
            "hosting_jurisdiction": "DE",
            "operator": "Acme Bank AG",
            "sovereignty_attestation": "on-prem-frankfurt-dc01",
        },
        emitter=sink,
    )
    p = r["payload"]
    assert p["hosting_jurisdiction"] == "DE"
    assert p["egress_disabled"] is True
    assert p["data_residency_confirmed"] is True
    assert verify_receipt(r) is True


def test_decorator_sync():
    sink = InMemoryEmitter()

    @lpr_track(
        article="50(2)",
        schema="generated_content/v1",
        model="luminous-base",
        emitter=sink,
    )
    def chat(prompt: str) -> str:
        return "antwort: " + prompt

    out = chat("hallo")
    assert out == "antwort: hallo"
    assert len(sink) == 1
    assert verify_receipt(sink.receipts[0]) is True


@pytest.mark.asyncio
async def test_decorator_async():
    sink = InMemoryEmitter()

    @lpr_track(
        article="50(2)",
        schema="generated_content/v1",
        model="luminous-base",
        emitter=sink,
    )
    async def chat(prompt: str) -> str:
        return "async-antwort: " + prompt

    out = await chat("hallo")
    assert out == "async-antwort: hallo"
    assert len(sink) == 1
    assert verify_receipt(sink.receipts[0]) is True


def test_emit_rejects_unknown_schema():
    with pytest.raises(KeyError):
        emit_receipt(
            article="50(2)",
            schema="not/a/schema",
            prompt_text="x",
            completion_text="y",
            model="luminous-base",
            emitter=InMemoryEmitter(),
        )
