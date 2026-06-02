"""LedgerProofCallbackHandler tests.

Asserts that:
  1. The callback fires and emits a receipt on on_llm_end.
  2. The emitted receipt envelope has the expected fields (schema_id,
     transcript_sha256, signature, public key, alg).
  3. No network is touched during signing / verification — we verify the
     receipt locally using only the embedded public key.
  4. GDPR validator rejects email-shaped deployer_id at construction.
"""

import base64
import uuid

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from langchain_core.outputs import Generation, LLMResult
from pydantic import ValidationError

from ledgerproof_langchain import LedgerProofCallbackHandler, QueueEmitter
from ledgerproof_langchain.canonical import canonical_encode
import hashlib


def _make_llm_result(text: str = "Hello, world.") -> LLMResult:
    return LLMResult(generations=[[Generation(text=text)]])


def test_callback_fires_and_emits_receipt():
    em = QueueEmitter()
    handler = LedgerProofCallbackHandler(deployer_id="acme-corp", emitter=em)
    rid = uuid.uuid4()

    handler.on_llm_start(
        serialized={"name": "test-llm", "kwargs": {"model": "gpt-4o-mini"}},
        prompts=["hello"],
        run_id=rid,
    )
    handler.on_llm_new_token("Hello", run_id=rid)
    handler.on_llm_new_token(", world.", run_id=rid)
    handler.on_llm_end(_make_llm_result(""), run_id=rid)

    assert em.queue.qsize() == 1
    envelope = em.queue.get_nowait()
    assert envelope["alg"] == "Ed25519"
    assert "body" in envelope
    assert "signature_ed25519" in envelope
    assert "public_key_ed25519" in envelope


def test_receipt_has_correct_fields():
    em = QueueEmitter()
    handler = LedgerProofCallbackHandler(
        deployer_id="acme-corp",
        schema="chatbot_session/v1",
        emitter=em,
    )
    rid = uuid.uuid4()
    handler.on_llm_start(
        serialized={"name": "x", "kwargs": {"model": "gpt-4o-mini"}},
        prompts=["hi"],
        run_id=rid,
    )
    handler.on_llm_end(_make_llm_result("Hi back."), run_id=rid)

    envelope = em.queue.get_nowait()
    body = envelope["body"]
    assert body["schema_id"] == "chatbot_session/v1"
    assert body["deployer_id"] == "acme-corp"
    assert body["model_identifier"] == "gpt-4o-mini"
    assert len(body["transcript_sha256"]) == 64
    assert body["run_id"] == str(rid)
    assert "timestamp_utc" in body


def test_no_network_during_verify():
    """Signature must verify offline using only the embedded public key."""
    em = QueueEmitter()
    handler = LedgerProofCallbackHandler(deployer_id="acme-corp", emitter=em)
    rid = uuid.uuid4()
    handler.on_llm_start(
        serialized={"name": "x", "kwargs": {"model": "test"}},
        prompts=["p"],
        run_id=rid,
    )
    handler.on_llm_end(_make_llm_result("o"), run_id=rid)

    envelope = em.queue.get_nowait()

    # Reconstruct the digest that was signed.
    body_bytes = canonical_encode(envelope["body"])
    body_digest = hashlib.sha256(body_bytes).digest()
    assert body_digest.hex() == envelope["body_sha256"]

    # Decode public key and signature (URL-safe base64 with stripped padding).
    def _b64u_decode(s: str) -> bytes:
        return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))

    pk_bytes = _b64u_decode(envelope["public_key_ed25519"])
    sig = _b64u_decode(envelope["signature_ed25519"])

    pk = Ed25519PublicKey.from_public_bytes(pk_bytes)
    # If this raises, the signature is invalid. No network involved.
    pk.verify(sig, body_digest)


def test_gdpr_validator_rejects_email_deployer_id():
    em = QueueEmitter()
    handler = LedgerProofCallbackHandler(deployer_id="alice@corp.example", emitter=em)
    rid = uuid.uuid4()
    handler.on_llm_start(
        serialized={"name": "x", "kwargs": {"model": "test"}},
        prompts=["p"],
        run_id=rid,
    )
    with pytest.raises(ValidationError):
        handler.on_llm_end(_make_llm_result("o"), run_id=rid)


def test_streaming_does_not_buffer_body():
    """The handler stores no token strings — only the running hash state."""
    em = QueueEmitter()
    handler = LedgerProofCallbackHandler(deployer_id="acme", emitter=em)
    rid = uuid.uuid4()
    handler.on_llm_start(
        serialized={"name": "x", "kwargs": {"model": "test"}},
        prompts=["p"],
        run_id=rid,
    )
    for tok in ["one ", "two ", "three"]:
        handler.on_llm_new_token(tok, run_id=rid)

    # Inspect the live run state: it must not contain a token buffer.
    state = handler._runs[str(rid)]
    assert not hasattr(state, "tokens")
    assert not hasattr(state, "buffer")
    handler.on_llm_end(_make_llm_result(""), run_id=rid)
