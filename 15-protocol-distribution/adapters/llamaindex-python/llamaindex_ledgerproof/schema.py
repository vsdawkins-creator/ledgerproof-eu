"""Pydantic v2 schemas for LedgerProof receipts emitted from LlamaIndex.

Three schemas, one per Article 50 use case our LlamaIndex surface covers:

- ``RagChatbotSessionReceipt`` (``rag_chatbot_session/v1``)
    Article 50(1) — disclosure receipt for a RAG chat session, with the retrieval
    context hashed (not stored verbatim, for GDPR data minimization).

- ``GeneratedContentReceipt`` (``generated_content/v1``)
    Article 50(2) — marking of AI-generated content (text, image, audio, video).

- ``RagSynthesizedResponseReceipt`` (``rag_synthesized_response/v1``)
    Article 50(1) with explicit source attribution — for cases where the
    deployer wants to evidence that a specific response was grounded in a
    specific set of retrieved documents.

GDPR notes (recital 26 / Art. 4(1)):

- ``deployer_id`` is a *legal entity* identifier (organization), not a natural
  person — kept structurally to avoid accidental PII overload.
- ``subject_pseudonym`` MUST be a pseudonym. We reject anything that looks like
  an email, a national ID, or a phone number. Hash on your side first.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# Patterns we refuse on subject_pseudonym / deployer_id — pseudonymize first.
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PHONE_RE = re.compile(r"^\+?\d[\d\s\-().]{6,}$")
# Loose national-ID heuristic: 8+ contiguous digits.
_LONG_DIGIT_RE = re.compile(r"\d{8,}")


def _reject_pii(value: str, field_name: str) -> str:
    """Best-effort PII guard. NOT a substitute for a real DPIA."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    s = value.strip()
    if _EMAIL_RE.match(s):
        raise ValueError(f"{field_name} looks like an email; pseudonymize before passing")
    if _PHONE_RE.match(s):
        raise ValueError(f"{field_name} looks like a phone number; pseudonymize before passing")
    if _LONG_DIGIT_RE.search(s):
        raise ValueError(
            f"{field_name} contains a long digit run that may be a national ID; pseudonymize first"
        )
    if len(s) > 256:
        raise ValueError(f"{field_name} exceeds 256 chars — use a hash/pseudonym")
    return s


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class _BaseReceipt(BaseModel):
    """Fields shared across every Article 50 receipt the adapter can emit."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        frozen=False,
    )

    schema_id: str
    schema_version: Literal["v1"] = "v1"
    receipt_id: str = Field(..., min_length=8, max_length=128)
    deployer_id: str
    occurred_at: datetime = Field(default_factory=_utcnow)
    article: str = Field(..., pattern=r"^50\((1|2|3|4)\)$")
    protocol_version: Literal["lpr/0.1"] = "lpr/0.1"

    @field_validator("deployer_id")
    @classmethod
    def _validate_deployer_id(cls, v: str) -> str:
        return _reject_pii(v, "deployer_id")


class RagChatbotSessionReceipt(_BaseReceipt):
    """``rag_chatbot_session/v1`` — Article 50(1) RAG chatbot disclosure.

    Captures the *fact* that a user interacted with an AI chatbot, with a hash
    of the retrieval context so a verifier can later confirm which corpus state
    was in play without exposing the documents themselves.
    """

    schema_id: Literal["rag_chatbot_session/v1"] = "rag_chatbot_session/v1"
    session_id: str = Field(..., min_length=4, max_length=128)
    subject_pseudonym: Optional[str] = Field(default=None, max_length=256)
    model_provider: str = Field(..., max_length=128)
    model_name: str = Field(..., max_length=256)
    retrieval_context_hash: str = Field(..., pattern=r"^[0-9a-f]{64}$")
    num_retrieved_chunks: int = Field(..., ge=0, le=10_000)
    transcript_hash: str = Field(..., pattern=r"^[0-9a-f]{64}$")
    disclosure_shown: bool = True

    @field_validator("subject_pseudonym")
    @classmethod
    def _validate_subject(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return _reject_pii(v, "subject_pseudonym")


class GeneratedContentReceipt(_BaseReceipt):
    """``generated_content/v1`` — Article 50(2) generated-content marking."""

    schema_id: Literal["generated_content/v1"] = "generated_content/v1"
    content_kind: Literal["text", "image", "audio", "video"] = "text"
    content_hash: str = Field(..., pattern=r"^[0-9a-f]{64}$")
    content_length_bytes: int = Field(..., ge=0)
    model_provider: str = Field(..., max_length=128)
    model_name: str = Field(..., max_length=256)
    marking_method: Literal["watermark", "metadata", "transcript", "none"] = "transcript"


class RagSynthesizedResponseReceipt(_BaseReceipt):
    """``rag_synthesized_response/v1`` — Article 50(1) with source attribution."""

    schema_id: Literal["rag_synthesized_response/v1"] = "rag_synthesized_response/v1"
    session_id: str = Field(..., min_length=4, max_length=128)
    query_hash: str = Field(..., pattern=r"^[0-9a-f]{64}$")
    response_hash: str = Field(..., pattern=r"^[0-9a-f]{64}$")
    source_document_hashes: list[str] = Field(default_factory=list, max_length=1000)
    model_provider: str = Field(..., max_length=128)
    model_name: str = Field(..., max_length=256)

    @field_validator("source_document_hashes")
    @classmethod
    def _validate_source_hashes(cls, v: list[str]) -> list[str]:
        pat = re.compile(r"^[0-9a-f]{64}$")
        for h in v:
            if not pat.match(h):
                raise ValueError(f"source_document_hashes entry not a sha256 hex: {h!r}")
        return v


# Convenience for downstream code that wants to enumerate supported schemas.
ALL_SCHEMAS: dict[str, type[_BaseReceipt]] = {
    "rag_chatbot_session/v1": RagChatbotSessionReceipt,
    "generated_content/v1": GeneratedContentReceipt,
    "rag_synthesized_response/v1": RagSynthesizedResponseReceipt,
}


def receipt_envelope(
    receipt: _BaseReceipt,
    signature_hex: str,
    public_key_hex: str,
    key_id: str,
) -> dict[str, Any]:
    """Wrap a signed receipt in the canonical envelope shape.

    The envelope is what the emitter writes out — it carries enough context for
    an offline verifier to reconstruct the canonical bytes and verify the
    Ed25519 signature.
    """
    return {
        "envelope_version": "lpr/0.1",
        "payload": receipt.model_dump(mode="json"),
        "signature": {
            "alg": "ed25519",
            "key_id": key_id,
            "public_key": public_key_hex,
            "sig": signature_hex,
        },
    }
