"""Tests for LedgerProofGeneratorWrapper using a mocked Haystack generator."""

import base64

from ledgerproof_haystack import (
    LedgerProofGeneratorWrapper,
    MemoryEmitter,
    canonical_cbor,
    generate_signing_key,
    verify_signature,
)


class _FakeGenerator:
    """Minimal stand-in for a Haystack 2.x generator."""

    model = "fake-llm-7b"

    def __init__(self, reply: str = "Antwort"):
        self.reply = reply
        self.calls = []

    def run(self, prompt: str | None = None):  # noqa: D401
        self.calls.append(prompt)
        return {"replies": [self.reply], "meta": [{"model": self.model}]}


def test_wrapper_emits_generated_content_receipt():
    key = generate_signing_key()
    mem = MemoryEmitter()
    inner = _FakeGenerator(reply="Generated answer in German.")
    wrapped = LedgerProofGeneratorWrapper(
        inner=inner, signing_key=key, deployer="acme-de", emitter=mem
    )
    result = wrapped.run(prompt="Erklären Sie GDPR.")
    # Inner's output flows through unchanged.
    assert result["replies"] == ["Generated answer in German."]
    assert len(mem) == 1
    rec = mem.records[0]["receipt"]
    assert rec["schema_id"] == "generated_content/v1"
    assert rec["generator_class"] == "_FakeGenerator"
    assert rec["model_id"] == "fake-llm-7b"


def test_wrapper_signature_verifies():
    key = generate_signing_key()
    mem = MemoryEmitter()
    inner = _FakeGenerator()
    wrapped = LedgerProofGeneratorWrapper(
        inner=inner, signing_key=key, deployer="d", emitter=mem
    )
    wrapped.run(prompt="x")
    env = mem.records[0]
    sig = base64.b64decode(env["signature_b64"])
    assert verify_signature(env["public_key_b64"], canonical_cbor(env["receipt"]), sig)


def test_wrapper_does_not_mutate_inner_output():
    key = generate_signing_key()
    mem = MemoryEmitter()
    inner = _FakeGenerator(reply="x")
    wrapped = LedgerProofGeneratorWrapper(
        inner=inner, signing_key=key, deployer="d", emitter=mem
    )
    result = wrapped.run(prompt="q")
    assert "replies" in result and result["replies"] == ["x"]


def test_streaming_builder_finalizes_and_signs():
    from ledgerproof_haystack import lpr_pipeline_callback

    key = generate_signing_key()
    mem = MemoryEmitter()
    cb, builder = lpr_pipeline_callback(
        signing_key=key,
        emitter=mem,
        deployer="acme-de",
        model_id="gpt-4o-mini",
        generator_class="OpenAIGenerator",
    )

    # Simulate StreamingChunk-like objects.
    class C:
        def __init__(self, c):
            self.content = c

    cb(C("Hallo "))
    cb(C("Welt"))
    env = builder.finalize()
    assert env["receipt"]["content_length"] == len("Hallo Welt".encode("utf-8"))
    sig = base64.b64decode(env["signature_b64"])
    assert verify_signature(env["public_key_b64"], canonical_cbor(env["receipt"]), sig)
    assert len(mem) == 1
