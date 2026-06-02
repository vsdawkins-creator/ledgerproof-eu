"""Sync + async client wrapper tests using mocked Aleph Alpha SDK objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

from ledgerproof_aleph_alpha import (
    InMemoryEmitter,
    LedgerProofAlephAlpha,
    LedgerProofAsyncAlephAlpha,
)


# --- minimal aleph-alpha-shaped fakes ---------------------------------------


@dataclass
class _FakeTextItem:
    text: str


@dataclass
class _FakePrompt:
    items: list[_FakeTextItem]


@dataclass
class _FakeRequest:
    prompt: _FakePrompt
    maximum_tokens: int = 64


@dataclass
class _FakeCompletion:
    completion: str


@dataclass
class _FakeResponse:
    completions: list[_FakeCompletion]
    model_version: str = "2024-09"


class _FakeSyncClient:
    def __init__(self, output: str = "auf wiedersehen") -> None:
        self._output = output
        self.calls: list[tuple[Any, dict[str, Any]]] = []

    def complete(self, request: Any, model: str, **kwargs: Any) -> _FakeResponse:
        self.calls.append((request, {"model": model, **kwargs}))
        return _FakeResponse(completions=[_FakeCompletion(self._output)])


class _FakeAsyncClient:
    def __init__(self, output: str = "guten tag") -> None:
        self._output = output

    async def complete(self, request: Any, model: str, **kwargs: Any) -> _FakeResponse:
        return _FakeResponse(completions=[_FakeCompletion(self._output)])


# --- sync wrapper -----------------------------------------------------------


def _make_request(text: str) -> _FakeRequest:
    return _FakeRequest(prompt=_FakePrompt(items=[_FakeTextItem(text=text)]))


def test_sync_wrapper_does_not_modify_response():
    fake = _FakeSyncClient(output="hallo welt")
    sink = InMemoryEmitter()
    client = LedgerProofAlephAlpha(fake, emitter=sink)
    resp = client.complete(_make_request("ping"), model="luminous-base")
    # C7: returned response is byte-identical to upstream
    assert resp.completions[0].completion == "hallo welt"
    assert resp.model_version == "2024-09"
    assert len(sink) == 1


def test_sync_wrapper_emits_signed_receipt():
    from ledgerproof_aleph_alpha import verify_receipt

    fake = _FakeSyncClient(output="x")
    sink = InMemoryEmitter()
    client = LedgerProofAlephAlpha(
        fake,
        emitter=sink,
        deployer_id="acme-de-frankfurt",
    )
    client.complete(_make_request("hi"), model="luminous-base")
    receipt = sink.receipts[0]
    assert verify_receipt(receipt) is True
    assert receipt["payload"]["model"] == "luminous-base"
    assert receipt["payload"]["model_version"] == "2024-09"
    assert receipt["payload"]["deployer_id"] == "acme-de-frankfurt"


def test_sync_wrapper_on_prem_extra_propagates():
    fake = _FakeSyncClient(output="x")
    sink = InMemoryEmitter()
    client = LedgerProofAlephAlpha(
        fake,
        article="50(1)",
        schema="on_prem_sovereign_deployment/v1",
        emitter=sink,
        extra={
            "hosting_jurisdiction": "DE",
            "operator": "Acme Bank AG",
            "sovereignty_attestation": "on-prem-frankfurt-dc01",
        },
    )
    client.complete(_make_request("hi"), model="luminous-supreme-control")
    p = sink.receipts[0]["payload"]
    assert p["schema_name"] == "on_prem_sovereign_deployment/v1"
    assert p["hosting_jurisdiction"] == "DE"
    assert p["operator"] == "Acme Bank AG"
    assert p["sovereignty_attestation"] == "on-prem-frankfurt-dc01"


def test_sync_wrapper_attribute_passthrough():
    fake = _FakeSyncClient()
    fake.weird_attr = 42  # type: ignore[attr-defined]
    client = LedgerProofAlephAlpha(fake)
    assert client.weird_attr == 42


# --- async wrapper ----------------------------------------------------------


@pytest.mark.asyncio
async def test_async_wrapper_does_not_modify_response():
    fake = _FakeAsyncClient(output="hi async")
    sink = InMemoryEmitter()
    client = LedgerProofAsyncAlephAlpha(fake, emitter=sink)
    resp = await client.complete(_make_request("ping"), model="luminous-base")
    assert resp.completions[0].completion == "hi async"
    assert len(sink) == 1


@pytest.mark.asyncio
async def test_async_wrapper_emits_signed_receipt():
    from ledgerproof_aleph_alpha import verify_receipt

    fake = _FakeAsyncClient(output="x")
    sink = InMemoryEmitter()
    client = LedgerProofAsyncAlephAlpha(fake, emitter=sink)
    await client.complete(_make_request("hi"), model="luminous-base")
    assert verify_receipt(sink.receipts[0]) is True
