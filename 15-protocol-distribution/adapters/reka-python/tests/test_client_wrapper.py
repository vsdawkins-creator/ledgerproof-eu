"""
Client wrapper tests using mocked Reka clients (no network).

We mock the inner `reka.client.Reka` / `AsyncReka` instances so the tests run
on a fresh venv without an API key. The wrapper only imports `from reka.client`
when constructing a default client; passing `client=...` skips that path.
"""

from __future__ import annotations

import asyncio
import base64
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from ledgerproof_reka import (
    LedgerProofAsyncReka,
    LedgerProofReka,
    QueueEmitter,
)
from ledgerproof_reka.canonical import canonical_encode
from ledgerproof_reka.signer import Ed25519Signer, verify


def _fake_response(text="Hello, world.", with_tool_use=False, response_id="resp_test_001"):
    """Build a SimpleNamespace shaped like a Reka ChatResponse."""
    tool_calls = []
    if with_tool_use:
        tool_calls.append(
            SimpleNamespace(name="bash", id="tu_test_1", arguments={"cmd": "ls"})
        )
    message = SimpleNamespace(content=text, tool_calls=tool_calls if tool_calls else None)
    first = SimpleNamespace(
        message=message,
        finish_reason="stop",
        tool_calls=tool_calls if tool_calls else None,
    )
    return SimpleNamespace(
        id=response_id,
        model="reka-flash-3.1",
        responses=[first],
        usage=SimpleNamespace(input_tokens=10, output_tokens=20),
    )


def _make_wrapper(captured, with_tool_use=False):
    fake_inner = MagicMock()
    fake_inner.chat.create.return_value = _fake_response(with_tool_use=with_tool_use)
    return LedgerProofReka(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )


def test_sync_create_emits_receipt_and_returns_response_unchanged():
    captured: list = []
    wrapper = _make_wrapper(captured)
    response = wrapper.chat.create(
        model="reka-flash-3.1",
        messages=[{"role": "user", "content": "Hi there"}],
    )
    # C7: response is passed through unchanged.
    assert response.id == "resp_test_001"
    assert response.responses[0].message.content == "Hello, world."

    assert len(captured) == 1
    signed = captured[0]
    assert signed["signature_alg"] == "ed25519"
    assert signed["receipt"]["deployer_id"] == "acme-eu-test"
    assert signed["receipt"]["schema"] == "chatbot_session/v1"
    assert signed["receipt"]["streaming"] is False
    assert signed["receipt"]["model"]["provider"] == "reka"
    assert signed["receipt"]["adapter"] == "ledgerproof-reka"
    roles = [c["role"] for c in signed["receipt"]["content_refs"]]
    assert "user" in roles and "assistant" in roles


def test_sync_create_with_tool_use_records_tool_calls():
    captured: list = []
    wrapper = _make_wrapper(captured, with_tool_use=True)
    wrapper.chat.create(
        model="reka-flash-3.1",
        messages=[{"role": "user", "content": "Run ls"}],
    )
    signed = captured[0]
    assert signed["receipt"]["tool_uses"][0]["tool_name"] == "bash"
    assert signed["receipt"]["tool_uses"][0]["tool_use_id"] == "tu_test_1"


def test_sync_create_with_image_input_promotes_to_multimodal_native():
    captured: list = []
    wrapper = _make_wrapper(captured)
    # 1x1 transparent PNG bytes, base64-encoded inline image content block.
    png_b64 = base64.b64encode(b"\x89PNG\r\n\x1a\nfakepayload").decode()
    wrapper.chat.create(
        model="reka-flash-3.1",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What is in this picture?"},
                    {
                        "type": "image",
                        "image": {"data": png_b64, "media_type": "image/png"},
                    },
                ],
            }
        ],
    )
    signed = captured[0]
    assert signed["receipt"]["schema"] == "multimodal_native_inference/v1"
    assert "text" in signed["receipt"]["input_modalities"]
    assert "image" in signed["receipt"]["input_modalities"]
    assert signed["receipt"]["media_refs"][0]["modality"] == "image"
    assert signed["receipt"]["media_refs"][0]["mime_type"] == "image/png"


def test_sync_create_with_video_input_promotes_to_video_understanding():
    captured: list = []
    wrapper = _make_wrapper(captured)
    video_b64 = base64.b64encode(b"\x00\x00\x00 ftypisom-fake-mp4").decode()
    wrapper.chat.create(
        model="reka-core",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Summarise this clip"},
                    {
                        "type": "video",
                        "video": {"data": video_b64, "media_type": "video/mp4"},
                    },
                ],
            }
        ],
    )
    signed = captured[0]
    assert signed["receipt"]["schema"] == "video_understanding/v1"
    assert "video" in signed["receipt"]["input_modalities"]
    assert signed["receipt"]["media_refs"][0]["modality"] == "video"


def test_video_url_only_block_is_hashed_by_uri_not_fetched():
    """C4: URL-only media refs MUST be hashed by URI, never dereferenced."""
    captured: list = []
    wrapper = _make_wrapper(captured)
    url = "https://example.com/promo.mp4"
    wrapper.chat.create(
        model="reka-core",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Watch and describe"},
                    {"type": "video", "url": url, "media_type": "video/mp4"},
                ],
            }
        ],
    )
    signed = captured[0]
    media = signed["receipt"]["media_refs"][0]
    assert media["modality"] == "video"
    # Hash must equal sha256(url-bytes), proving we didn't fetch.
    import hashlib

    assert media["source_uri_sha256_hex"] == hashlib.sha256(url.encode()).hexdigest()


def test_sync_streaming_emits_receipt_with_incremental_hash():
    captured: list = []

    def fake_create_stream(**kwargs):
        chunks = ["Hel", "lo, ", "world."]

        def _gen():
            for c in chunks:
                msg = SimpleNamespace(content=c)
                first = SimpleNamespace(chunk=msg)
                yield SimpleNamespace(
                    id="resp_stream_001",
                    model="reka-flash-3.1",
                    responses=[first],
                )

        return _gen()

    fake_inner = MagicMock()
    fake_inner.chat.create_stream = fake_create_stream

    wrapper = LedgerProofReka(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )
    stream = wrapper.chat.create_stream(
        model="reka-flash-3.1",
        messages=[{"role": "user", "content": "Hi"}],
    )
    collected: list[str] = []
    for chunk in stream:
        delta = chunk.responses[0].chunk.content
        collected.append(delta)
    assert "".join(collected) == "Hello, world."

    assert len(captured) == 1
    signed = captured[0]
    assert signed["receipt"]["streaming"] is True
    asst = next(c for c in signed["receipt"]["content_refs"] if c["role"] == "assistant")
    assert asst["byte_length"] == len("Hello, world.".encode("utf-8"))


def test_async_create_emits_receipt():
    captured: list = []

    fake_inner = MagicMock()
    fake_inner.chat.create = AsyncMock(return_value=_fake_response())

    wrapper = LedgerProofAsyncReka(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )

    async def _run():
        response = await wrapper.chat.create(
            model="reka-flash-3.1",
            messages=[{"role": "user", "content": "Hi async"}],
        )
        assert response.id == "resp_test_001"

    asyncio.run(_run())

    assert len(captured) == 1
    assert captured[0]["receipt"]["deployer_id"] == "acme-eu-test"


def test_signature_verifies_with_published_public_key():
    """C4: offline verification works given the public key bytes."""
    captured: list = []
    signer = Ed25519Signer()
    fake_inner = MagicMock()
    fake_inner.chat.create.return_value = _fake_response()
    wrapper = LedgerProofReka(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=signer,
    )
    wrapper.chat.create(
        model="reka-flash-3.1",
        messages=[{"role": "user", "content": "Verify me"}],
    )
    signed = captured[0]
    canonical_bytes = canonical_encode(signed["receipt"])
    sig = base64.b64decode(signed["signature_b64"])
    assert verify(signer.public_key_bytes(), canonical_bytes, sig)


def test_wrapper_swallows_emitter_failure_and_returns_response():
    """C7: receipt emission failure MUST NOT break the response path."""

    def boom(_):
        raise RuntimeError("emitter broken")

    fake_inner = MagicMock()
    fake_inner.chat.create.return_value = _fake_response()
    wrapper = LedgerProofReka(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(boom),  # QueueEmitter itself swallows; layer in something nastier:
        signer=Ed25519Signer(),
    )

    # Now patch the emitter to raise OUTSIDE QueueEmitter's swallow:
    class HardFailEmitter:
        def emit(self, _):
            raise RuntimeError("hard-fail")

    wrapper._emitter = HardFailEmitter()
    response = wrapper.chat.create(
        model="reka-flash-3.1",
        messages=[{"role": "user", "content": "Don't break"}],
    )
    assert response.id == "resp_test_001"
