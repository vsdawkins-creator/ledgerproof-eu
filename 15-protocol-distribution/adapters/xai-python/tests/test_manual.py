"""Manual emit_receipt tests."""

import hashlib
import queue
from types import SimpleNamespace

from ledgerproof_xai import QueueEmitter, emit_receipt


def _fake_response(text="hi from grok", model="grok-2-latest"):
    message = SimpleNamespace(role="assistant", content=text)
    choice = SimpleNamespace(index=0, message=message, finish_reason="stop")
    return SimpleNamespace(id="grok-cmpl-99", model=model, choices=[choice])


def test_manual_emit_basic_receipt():
    q: queue.Queue = queue.Queue()
    resp = _fake_response()
    env = emit_receipt(
        resp,
        deployer_id="urn:eu:deployer:acme",
        messages=[{"role": "user", "content": "hello"}],
        emitter=QueueEmitter(q),
    )
    assert env["receipt"]["model_id"] == "grok-2-latest"
    assert env["receipt"]["model_provider"] == "xai"
    assert env["adapter"]["name"] == "ledgerproof-xai"
    assert q.get_nowait() == env


def test_manual_emit_realtime_data_schema_with_extra_fields():
    q: queue.Queue = queue.Queue()
    resp = _fake_response(text="The latest from X is...")
    sources_hash = hashlib.sha256(b"[\"https://x.com/post/1\"]").hexdigest()
    env = emit_receipt(
        resp,
        deployer_id="urn:eu:deployer:acme",
        messages=[{"role": "user", "content": "news?"}],
        regulatory_context={"schema": "realtime_data_inference/v1"},
        extra_fields={
            "realtime_data_used": True,
            "realtime_sources_sha256": sources_hash,
            "public_interest_text": True,
        },
        emitter=QueueEmitter(q),
    )
    assert env["receipt"]["schema_id"] == "realtime_data_inference/v1"
    assert env["receipt"]["realtime_sources_sha256"] == sources_hash
    assert env["receipt"]["realtime_data_used"] is True


def test_manual_emit_vision_schema_with_image_hash():
    q: queue.Queue = queue.Queue()
    resp = _fake_response(text="I see two cats.", model="grok-2-vision")
    img_hash = hashlib.sha256(b"PNGpayload").hexdigest()
    env = emit_receipt(
        resp,
        deployer_id="urn:eu:deployer:acme",
        messages=[{"role": "user", "content": "look"}],
        regulatory_context={"schema": "vision_inference/v1"},
        extra_fields={
            "image_input_sha256": img_hash,
            "image_count": 2,
            "content_modality": "image",
        },
        emitter=QueueEmitter(q),
    )
    assert env["receipt"]["schema_id"] == "vision_inference/v1"
    assert env["receipt"]["image_input_sha256"] == img_hash
    assert env["receipt"]["image_count"] == 2
