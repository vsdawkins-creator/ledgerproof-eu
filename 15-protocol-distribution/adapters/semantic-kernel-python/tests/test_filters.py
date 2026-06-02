"""Filter behavior tests.

Semantic Kernel is heavy and may not be available in CI; we mock the
filter-context shape (function metadata, arguments, result) and verify the
filter emits a structurally valid signed receipt with the right schema.

We import the filter module via a path-based fallback so the test works
even when `semantic_kernel` is not installed (the filters detect that and
raise — these tests exercise the receipt-building path through
`_build_and_emit` directly to keep them hermetic).
"""

import asyncio
import base64

import pytest

from ledgerproof_semantic_kernel import filters as filters_module
from ledgerproof_semantic_kernel.emitter import QueueEmitter
from ledgerproof_semantic_kernel.signer import Ed25519Signer


class _FakeMeta:
    def __init__(self, plugin_name, name):
        self.plugin_name = plugin_name
        self.name = name


class _FakeFunction:
    def __init__(self, plugin, name):
        self.metadata = _FakeMeta(plugin, name)


class _FakeResult:
    def __init__(self, value):
        self.value = value


class _FakeCtx:
    def __init__(self, plugin, function, args, result):
        self.function = _FakeFunction(plugin, function)
        self.arguments = args
        self.result = result


def _force_sk_available(monkeypatch):
    monkeypatch.setattr(filters_module, "_SK_AVAILABLE", True)


def test_function_filter_emits_receipt(monkeypatch):
    _force_sk_available(monkeypatch)
    q = QueueEmitter()
    f = filters_module.LedgerProofFunctionFilter(
        deployer_id="acme-001",
        emitter=q,
        signer=Ed25519Signer(),
    )

    ctx = _FakeCtx(
        plugin="weather",
        function="get_weather",
        args={"city": "Paris"},
        result=_FakeResult("Sunny in Paris"),
    )

    async def _noop_next(_):
        return None

    asyncio.run(f.on_function_invocation(ctx, _noop_next))
    env = q.queue.get_nowait()
    body = env["body"]
    assert body["schema_id"] == "agent_function_invocation/v1"
    assert body["plugin_name"] == "weather"
    assert body["function_name"] == "get_weather"
    assert body["argument_names"] == ["city"]
    assert body["is_auto_invoked"] is False
    # Signature decodes to 64 raw bytes.
    pad = "=" * (-len(env["signature_ed25519"]) % 4)
    sig = base64.urlsafe_b64decode(env["signature_ed25519"] + pad)
    assert len(sig) == 64


def test_auto_function_filter_marks_auto_invoked(monkeypatch):
    _force_sk_available(monkeypatch)
    q = QueueEmitter()
    f = filters_module.LedgerProofAutoFunctionFilter(
        deployer_id="acme-agent",
        emitter=q,
        signer=Ed25519Signer(),
    )

    ctx = _FakeCtx(
        plugin="tools",
        function="lookup",
        args={"q": "weather"},
        result=_FakeResult("ok"),
    )
    # AutoFunctionInvocationContext exposes result via function_result.
    ctx.function_result = ctx.result

    async def _noop_next(_):
        return None

    asyncio.run(f.on_auto_function_invocation(ctx, _noop_next))
    env = q.queue.get_nowait()
    assert env["body"]["is_auto_invoked"] is True


def test_filter_does_not_raise_when_metadata_missing(monkeypatch):
    """Side-channel invariant: malformed context must not break invocation."""
    _force_sk_available(monkeypatch)
    q = QueueEmitter()
    f = filters_module.LedgerProofFunctionFilter(
        deployer_id="acme-001", emitter=q, signer=Ed25519Signer()
    )

    class _Bad:
        pass

    async def _noop_next(_):
        return None

    # Must not raise even though context has no .function / .arguments.
    asyncio.run(f.on_function_invocation(_Bad(), _noop_next))
