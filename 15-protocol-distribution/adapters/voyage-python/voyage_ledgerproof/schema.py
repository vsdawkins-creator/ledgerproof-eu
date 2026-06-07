"""
Receipt schemas for Article 50 evidence — Voyage AI variant.

Voyage AI is upstream RAG infrastructure (embeddings + rerank, owned by MongoDB).
Embeddings and rerank scores are not direct Article 50(1) chat surfaces, but they
ARE the evidence-trail substrate for any RAG pipeline whose downstream chatbot
output IS under Article 50. The schemas here let a deployer bind embedding +
rerank evidence to the downstream chat session, so a regulator (or auditor) can
follow the chain:

    user query
      -> Voyage embedding(s) (vector hash bound in embedding_inference/v1)
      -> Voyage rerank result(s) (relevance scores bound in rerank_inference/v1)
      -> downstream chatbot response (bound in rag_pipeline_evidence/v1)

Three schemas:
  - embedding_inference/v1 — Article 50 supporting infrastructure. Binds the
    SHA-256 of each input string, the model_id, the input_type
    ("document"|"query"|None), and a SHA-256 of the canonicalized output vector
    (float64 big-endian). Not itself an Article 50(1) artifact — it is the
    retrieval-side substrate that a downstream Article 50(1) receipt can
    reference.
  - rerank_inference/v1 — Article 50 supporting infrastructure. Binds the query
    hash, the candidate document hashes, the rerank model_id, and the per-
    document relevance scores + final ranking order. Lets an auditor verify
    after-the-fact that the documents fed to the downstream chatbot were
    chosen by exactly this rerank pass over exactly these candidates.
  - rag_pipeline_evidence/v1 — Article 50(1) variant. Captures the full
    embed -> rerank -> downstream-chat chain, binding upstream
    embedding_inference + rerank_inference receipt IDs (or hashes) into a
    session-level signed receipt. Strategically important because most EU
    enterprise AI deployments under Article 50 enforcement (2 Aug 2026) are
    RAG-shaped, and the regulator's first question on incident response is
    "what sources did the model see?".

GDPR guardrail: receipts MUST NOT contain raw input text, raw documents, or raw
embedding vectors. Content is referenced via SHA-256 hashes only. Free-text
fields are length-bounded. Document IDs are bounded character sets.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

SchemaName = Literal[
    "embedding_inference/v1",
    "rerank_inference/v1",
    "rag_pipeline_evidence/v1",
]

# Pattern allowing short bounded identifiers — no free-form PII.
_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:\-/+@]{1,128}$")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class _Base(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=False,
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class VoyageModelRef(_Base):
    """Reference to the Voyage AI model used."""

    provider: Literal["voyage"] = "voyage"
    model_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    # Voyage assigns no per-request response ID; we synthesize a UUID at emit time
    # so receipts can be cross-referenced.
    response_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    input_type: Literal["document", "query", "none"] | None = None
    output_dtype: Annotated[str, StringConstraints(max_length=32)] | None = None
    total_tokens: int | None = Field(default=None, ge=0)


class EmbeddingRef(_Base):
    """
    Reference to a single embedding produced by a Voyage embed call.

    Binds:
      - input_sha256_hex   — SHA-256 of the input string (UTF-8 bytes)
      - input_byte_length  — UTF-8 byte length of the input
      - vector_sha256_hex  — SHA-256 of the canonical byte representation
                             (big-endian float64 IEEE-754) of the embedding
      - vector_dim         — embedding dimension (e.g. 1024 for voyage-3-large)

    Raw text and raw vectors are NEVER stored.
    """

    input_sha256_hex: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    input_byte_length: int = Field(ge=0)
    vector_sha256_hex: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    vector_dim: int = Field(ge=1)
    input_index: int = Field(ge=0)


class RerankResultRef(_Base):
    """
    Reference to a single rerank result.

    Binds the candidate document hash, its post-rerank position, the relevance
    score, and the original-list index Voyage reported (`result.index`).
    """

    document_id: Annotated[str, StringConstraints(min_length=1, max_length=256)] | None = None
    document_sha256_hex: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    document_byte_length: int = Field(ge=0)
    original_index: int = Field(ge=0)
    rerank_position: int = Field(ge=0)
    relevance_score: float = Field(ge=0.0, le=1.0)


class UpstreamReceiptRef(_Base):
    """
    Pointer to an upstream embedding_inference/v1 or rerank_inference/v1 receipt
    referenced by a rag_pipeline_evidence/v1 receipt.

    The referenced receipt's canonical-CBOR SHA-256 binds it cryptographically;
    the verifier can recompute this hash from a stored upstream signed receipt
    and confirm the chain.
    """

    schema_name: Literal["embedding_inference/v1", "rerank_inference/v1"]
    receipt_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    receipt_canonical_sha256_hex: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]


class DownstreamChatRef(_Base):
    """
    Reference to the downstream chatbot turn the RAG pipeline fed.

    The downstream chat receipt (e.g. ledgerproof-openai, ledgerproof-anthropic,
    ledgerproof-cohere) is bound by its receipt_id + canonical hash. This is the
    chain link that makes rag_pipeline_evidence/v1 an Article 50(1) artifact:
    the downstream chat turn is the actual user-facing AI interaction.
    """

    downstream_adapter: Annotated[str, StringConstraints(min_length=1, max_length=64)]
    downstream_receipt_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    downstream_receipt_canonical_sha256_hex: Annotated[
        str, StringConstraints(pattern=r"^[0-9a-f]{64}$")
    ]
    user_query_sha256_hex: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    assistant_response_sha256_hex: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")] | None = None


class RegulatoryContext(_Base):
    """Deployer-supplied regulatory metadata."""

    article_50_paragraph: Literal["1", "2", "3", "4", "supporting"]
    deployer_jurisdiction: Annotated[str, StringConstraints(min_length=2, max_length=8)]
    end_user_disclosure_made: bool
    notes: Annotated[str, StringConstraints(max_length=512)] | None = None


class ReceiptV1(_Base):
    """Common envelope for all v1 Voyage-adapter receipts."""

    schema_name: SchemaName = Field(alias="schema")
    schema_version: Literal[1] = 1
    receipt_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    deployer_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    issued_at: datetime = Field(default_factory=_utcnow)
    model: VoyageModelRef
    regulatory_context: RegulatoryContext

    # Schema-specific payloads — only one will be populated per receipt.
    embeddings: list[EmbeddingRef] = Field(default_factory=list)
    rerank_query_sha256_hex: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")] | None = None
    rerank_query_byte_length: int | None = Field(default=None, ge=0)
    rerank_results: list[RerankResultRef] = Field(default_factory=list)
    upstream_receipts: list[UpstreamReceiptRef] = Field(default_factory=list)
    downstream_chat: DownstreamChatRef | None = None

    adapter: Annotated[str, StringConstraints(max_length=64)] = "ledgerproof-voyage"
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

    def to_payload(self) -> dict[str, Any]:
        """Dump the receipt to a JSON/CBOR-ready dict with stable key ordering."""
        return self.model_dump(mode="json", by_alias=True, exclude_none=False)


def build_embedding_inference_receipt(**kwargs: Any) -> ReceiptV1:
    """Article 50 supporting-infrastructure receipt for a Voyage embed call."""
    receipt = ReceiptV1(schema="embedding_inference/v1", **kwargs)
    if not receipt.embeddings:
        raise ValueError(
            "embedding_inference/v1 requires at least one EmbeddingRef in `embeddings`"
        )
    return receipt


def build_rerank_inference_receipt(**kwargs: Any) -> ReceiptV1:
    """Article 50 supporting-infrastructure receipt for a Voyage rerank call."""
    receipt = ReceiptV1(schema="rerank_inference/v1", **kwargs)
    if not receipt.rerank_results:
        raise ValueError(
            "rerank_inference/v1 requires at least one RerankResultRef in `rerank_results`"
        )
    if receipt.rerank_query_sha256_hex is None:
        raise ValueError(
            "rerank_inference/v1 requires rerank_query_sha256_hex (hash of the query string)"
        )
    return receipt


def build_rag_pipeline_evidence_receipt(**kwargs: Any) -> ReceiptV1:
    """
    Article 50(1) variant — full RAG pipeline evidence.

    Binds one or more upstream embedding_inference / rerank_inference receipts to
    a downstream chatbot turn captured by a sibling LedgerProof chat adapter.
    """
    receipt = ReceiptV1(schema="rag_pipeline_evidence/v1", **kwargs)
    if not receipt.upstream_receipts:
        raise ValueError(
            "rag_pipeline_evidence/v1 requires at least one upstream_receipts entry"
        )
    if receipt.downstream_chat is None:
        raise ValueError(
            "rag_pipeline_evidence/v1 requires downstream_chat (the actual Article 50(1) turn)"
        )
    return receipt
