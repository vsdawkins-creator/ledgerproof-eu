"""Chat-service wrapper: non-streaming and stream-aware paths."""

import asyncio
import base64

from ledgerproof_semantic_kernel.chat_service_wrapper import LedgerProofChatService
from ledgerproof_semantic_kernel.emitter import QueueEmitter
from ledgerproof_semantic_kernel.signer import Ed25519Signer


class _FakeMsg:
    def __init__(self, content):
        self.content = content


class _FakeHistory:
    def __init__(self, messages):
        self.messages = messages


class _FakeInner:
    ai_model_id = "gpt-4o-mini"

    async def get_chat_message_content(self, chat_history, settings=None, **kwargs):
        return _FakeMsg("Hello world")

    async def get_streaming_chat_message_content(
        self, chat_history, settings=None, **kwargs
    ):
        for token in ["Hel", "lo ", "wor", "ld"]:
            yield _FakeMsg(token)


def test_non_streaming_emits_single_receipt():
    q = QueueEmitter()
    service = LedgerProofChatService(
        _FakeInner(),
        deployer_id="acme-001",
        emitter=q,
        signer=Ed25519Signer(),
    )

    async def run():
        return await service.get_chat_message_content(
            chat_history=_FakeHistory([_FakeMsg("Hi")]),
        )

    msg = asyncio.run(run())
    assert msg.content == "Hello world"
    env = q.queue.get_nowait()
    body = env["body"]
    assert body["schema_id"] == "chatbot_session/v1"
    assert body["model_identifier"] == "gpt-4o-mini"
    assert body["disclosure_shown"] is True
    pad = "=" * (-len(env["signature_ed25519"]) % 4)
    assert len(base64.urlsafe_b64decode(env["signature_ed25519"] + pad)) == 64


def test_streaming_emits_single_receipt_after_stream_close():
    q = QueueEmitter()
    service = LedgerProofChatService(
        _FakeInner(),
        deployer_id="acme-001",
        emitter=q,
        signer=Ed25519Signer(),
    )

    async def run():
        out = []
        async for chunk in service.get_streaming_chat_message_content(
            chat_history=_FakeHistory([_FakeMsg("Hi")]),
        ):
            out.append(chunk.content)
        return "".join(out)

    s = asyncio.run(run())
    assert s == "Hello world"
    assert q.queue.qsize() == 1
    env = q.queue.get_nowait()
    assert env["body"]["schema_id"] == "chatbot_session/v1"


def test_azure_enterprise_extra_fields_propagate():
    q = QueueEmitter()
    service = LedgerProofChatService(
        _FakeInner(),
        deployer_id="acme-001",
        schema="azure_enterprise_session/v1",
        emitter=q,
        signer=Ed25519Signer(),
        extra={
            "tenant_id": "00000000-0000-0000-0000-000000000000",
            "subscription_scope": "sub/abc",
            "deployment_region": "westeurope",
        },
    )

    async def run():
        return await service.get_chat_message_content(
            chat_history=_FakeHistory([_FakeMsg("Hi")]),
        )

    asyncio.run(run())
    body = q.queue.get_nowait()["body"]
    assert body["tenant_id"] == "00000000-0000-0000-0000-000000000000"
    assert body["deployment_region"] == "westeurope"
    assert body["schema_id"] == "azure_enterprise_session/v1"


def test_transparent_attribute_delegation():
    service = LedgerProofChatService(
        _FakeInner(), deployer_id="acme-001", emitter=QueueEmitter()
    )
    assert service.ai_model_id == "gpt-4o-mini"
