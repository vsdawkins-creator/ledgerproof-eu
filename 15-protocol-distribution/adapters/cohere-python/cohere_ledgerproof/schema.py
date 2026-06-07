"""
Receipt schemas for Article 50 evidence — Cohere variant.

Four schemas:
  - chatbot_session/v1 — Article 50(1), direct chat interactions (ClientV2.chat)
  - generated_content/v1 — Article 50(2), synthetic content generation
  - rag_response/v1 — Article 50(1) variant: chat with retrieved-document attestation
    (binds the SHA-256 of each retrieved document and Rerank score, enabling
    after-the-fact verification that the model was actually grounded on the cited
    sources — strategically important for EU enterprise RAG pipelines using
    Cohere Embed + Rerank)
  - multilingual_disclosure/v1 — Article 50(1) variant: captures the natural
    language of the end-user disclosure ("Sie chatten mit einer KI", "Vous
    discutez avec une IA", etc.). Strategically relevant because Article 50(5)
    requires disclosures in a language the recipient understands, and EU
    deployers operating cross-border need to demonstrate per-jurisdiction
    language compliance. Cohere's strength in multilingual generation makes
    this a natural surface.

GDPR guardrail: receipts MUST NOT contain raw prompt or response text by default.
Content is referenced via SHA-256 hashes only. Free-text fields are length-bounded.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

SchemaName = Literal[
    "chatbot_session/v1",
    "generated_content/v1",
    "rag_response/v1",
    "multilingual_disclosure/v1",
]

# Pattern allowing short bounded identifiers — no free-form PII.
_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:\-/+@]{1,128}$")

# BCP-47-ish language tag — bounded, conservative.
_LANG_PATTERN = re.compile(r"^[A-Za-z]{2,3}(-[A-Za-z0-9]{2,8})*$")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class _Base(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=False,
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class ModelRef(_Base):
    """Reference to the AI system used (Cohere-side)."""

    provider: Literal["cohere"] = "cohere"
    model_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    response_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    finish_reason: Annotated[str, StringConstraints(max_length=64)] | None = None
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)


class ContentRef(_Base):
    """SHA-256 reference to message content. Raw text NEVER stored in receipts."""

    sha256_hex: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    byte_length: int = Field(ge=0)
    role: Literal["user", "assistant", "system", "tool"]


class ToolUseRef(_Base):
    """Tool call binding (Cohere tool use)."""

    tool_name: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    tool_call_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    input_sha256_hex: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    output_sha256_hex: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")] | None = None


class RetrievedDocumentRef(_Base):
    """
    Reference to a single document retrieved by an upstream retriever (Embed)
    and optionally reranked (Rerank). Binds document identity, content hash,
    and the rerank relevance score that determined inclusion in the prompt.

    GDPR: document_id is bounded; raw text is NEVER stored — only its hash.
    """

    document_id: Annotated[str, StringConstraints(min_length=1, max_length=256)]
    sha256_hex: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    byte_length: int = Field(ge=0)
    rerank_relevance_score: float | None = Field(default=None, ge=0.0, le=1.0)
    rerank_index: int | None = Field(default=None, ge=0)
    source_uri: Annotated[str, StringConstraints(max_length=512)] | None = None


class DisclosureRef(_Base):
    """
    Reference to the end-user disclosure shown to the natural person, for
    multilingual_disclosure/v1 receipts. Captures the BCP-47 language tag and
    a SHA-256 of the exact disclosure string presented (raw text NOT stored).

    Article 50(5): disclosure must be in a language understandable to the
    recipient. This schema lets deployers prove which language was actually
    shown without storing the user's UI locale or other PII.
    """

    language_tag: Annotated[str, StringConstraints(min_length=2, max_length=16)]
    disclosure_sha256_hex: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    disclosure_byte_length: int = Field(ge=0)
    disclosure_channel: Annotated[str, StringConstraints(max_length=64)] | None = None

    @field_validator("language_tag")
    @classmethod
    def _validate_lang(cls, v: str) -> str:
        if not _LANG_PATTERN.match(v):
            raise ValueError(
                f"language_tag {v!r} is not a valid BCP-47-style tag (e.g. 'de', 'fr-FR')"
            )
        return v


class RegulatoryContext(_Base):
    """Deployer-supplied regulatory metadata."""

    article_50_paragraph: Literal["1", "2", "3", "4"]
    deployer_jurisdiction: Annotated[str, StringConstraints(min_length=2, max_length=8)]
    end_user_disclosure_made: bool
    notes: Annotated[str, StringConstraints(max_length=512)] | None = None


class ReceiptV1(_Base):
    """Common envelope for all v1 receipts."""

    schema_name: SchemaName = Field(alias="schema")
    schema_version: Literal[1] = 1
    receipt_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    deployer_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    issued_at: datetime = Field(default_factory=_utcnow)
    model: ModelRef
    content_refs: list[ContentRef]
    regulatory_context: RegulatoryContext
    tool_uses: list[ToolUseRef] = Field(default_factory=list)
    retrieved_documents: list[RetrievedDocumentRef] = Field(default_factory=list)
    disclosure: DisclosureRef | None = None
    streaming: bool = False
    adapter: Annotated[str, StringConstraints(max_length=64)] = "ledgerproof-cohere"
    adapter_version: Annotated[str, StringConstraints(max_length=32)] = "0.1.0"

    @field_validator("deployer_id", "receipt_id")
    @classmethod
    def _validate_id(cls, v: str) -> str:
        if not _ID_PATTERN.match(v):
            raise ValueError(
                f"identifier {v!r} contains disallowed characters; "
                "use only [A-Za-z0-9._:-/+@] up to 128 chars"
            )
        return v

    @field_validator("content_refs")
    @classmethod
    def _at_least_one_content_ref(cls, v: list[ContentRef]) -> list[ContentRef]:
        if not v:
            raise ValueError("receipt must reference at least one piece of content")
        return v

    def to_payload(self) -> dict[str, Any]:
        """Dump the receipt to a JSON/CBOR-ready dict with stable key ordering."""
        return self.model_dump(mode="json", by_alias=True, exclude_none=False)


def build_chatbot_session_receipt(**kwargs: Any) -> ReceiptV1:
    return ReceiptV1(schema="chatbot_session/v1", **kwargs)


def build_generated_content_receipt(**kwargs: Any) -> ReceiptV1:
    return ReceiptV1(schema="generated_content/v1", **kwargs)


def build_rag_response_receipt(**kwargs: Any) -> ReceiptV1:
    """Article 50(1) variant — chat grounded on retrieved documents (Embed + Rerank)."""
    receipt = ReceiptV1(schema="rag_response/v1", **kwargs)
    if not receipt.retrieved_documents:
        raise ValueError(
            "rag_response/v1 requires at least one retrieved_documents entry; "
            "use chatbot_session/v1 for non-RAG chat"
        )
    return receipt


def build_multilingual_disclosure_receipt(**kwargs: Any) -> ReceiptV1:
    """Article 50(1) variant — binds the language of the disclosure shown to the user."""
    receipt = ReceiptV1(schema="multilingual_disclosure/v1", **kwargs)
    if receipt.disclosure is None:
        raise ValueError(
            "multilingual_disclosure/v1 requires a disclosure field "
            "(DisclosureRef with language_tag + hash of disclosure text)"
        )
    return receipt
