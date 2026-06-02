"""Pydantic schemas for LedgerProof Haystack receipts.

Schemas implement EU AI Act Article 50 obligations:
  - rag_pipeline_session/v1     -> Art. 50(1) full RAG pipeline trace
  - generated_content/v1        -> Art. 50(2) AI-generated content marking
  - haystack_node_receipt/v1    -> per-component (any pipeline node)
  - editorial_pipeline_review/v1-> Art. 50(4) editorial/public-interest text

C1: nothing here claims regulator endorsement or Art. 40 presumption.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

# ---------------------------------------------------------------------------
# GDPR PII heuristics — refuse common PII patterns unless lawful_basis given.
# ---------------------------------------------------------------------------

_PII_PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "iban": re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b"),
    "bic": re.compile(r"\b[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?\b"),
    # German Steuer-Identifikationsnummer is 11 digits
    "de_steuer_id": re.compile(r"\b\d{11}\b"),
    # Generic national ID-ish pattern
    "national_id_hint": re.compile(r"\b[A-Z]{1,3}\d{6,12}\b"),
}


def _looks_like_pii(value: str) -> Optional[str]:
    for label, pat in _PII_PATTERNS.items():
        if pat.search(value):
            return label
    return None


# ---------------------------------------------------------------------------
# Shared envelope fields.
# ---------------------------------------------------------------------------


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class _ReceiptBase(BaseModel):
    """Common envelope shared by every Haystack receipt schema."""

    receipt_id: str
    schema_id: str
    protocol: Literal["lpr/1"] = "lpr/1"
    issued_at: str = Field(default_factory=_utcnow_iso)
    deployer: str
    key_id: str
    adapter: str = "ledgerproof-haystack"
    gdpr_lawful_basis: Optional[str] = None

    @field_validator("deployer")
    @classmethod
    def _no_empty_deployer(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("deployer must be a non-empty identifier")
        return v.strip()

    @model_validator(mode="after")
    def _scan_pii(self) -> "_ReceiptBase":
        if self.gdpr_lawful_basis:
            return self
        for field_name, value in self.model_dump().items():
            if isinstance(value, str) and field_name not in {
                "receipt_id",
                "schema_id",
                "protocol",
                "issued_at",
                "deployer",
                "key_id",
                "adapter",
            }:
                hit = _looks_like_pii(value)
                if hit:
                    raise ValueError(
                        f"Field '{field_name}' looks like PII ({hit}); "
                        "set gdpr_lawful_basis to acknowledge processing basis."
                    )
        return self


# ---------------------------------------------------------------------------
# RAG pipeline session — Art. 50(1)
# ---------------------------------------------------------------------------


class RagPipelineSessionV1(_ReceiptBase):
    """Article 50(1) — user-facing disclosure that a RAG pipeline ran."""

    schema_id: Literal["rag_pipeline_session/v1"] = "rag_pipeline_session/v1"
    pipeline_name: str
    pipeline_hash: str  # canonical hash of the Pipeline DAG
    component_count: int = Field(ge=1)
    retrieved_doc_count: int = Field(ge=0)
    query_hash: str  # sha256 of normalized query
    answer_hash: str  # sha256 of generated answer
    model_id: str
    user_facing_disclosure_shown: bool = True

    @field_validator("pipeline_hash", "query_hash", "answer_hash")
    @classmethod
    def _hex64(cls, v: str) -> str:
        if not (len(v) == 64 and all(c in "0123456789abcdef" for c in v)):
            raise ValueError("must be a 64-char lowercase hex SHA-256 digest")
        return v


# ---------------------------------------------------------------------------
# Generated content — Art. 50(2)
# ---------------------------------------------------------------------------


class GeneratedContentV1(_ReceiptBase):
    """Article 50(2) — AI-generated content marking."""

    schema_id: Literal["generated_content/v1"] = "generated_content/v1"
    content_type: Literal["text", "image", "audio", "video"] = "text"
    content_hash: str
    content_length: int = Field(ge=0)
    model_id: str
    generator_class: str  # e.g. "OpenAIGenerator", "AnthropicGenerator"
    machine_readable_mark: str = "C2PA-or-equivalent"

    @field_validator("content_hash")
    @classmethod
    def _hex64(cls, v: str) -> str:
        if not (len(v) == 64 and all(c in "0123456789abcdef" for c in v)):
            raise ValueError("must be a 64-char lowercase hex SHA-256 digest")
        return v


# ---------------------------------------------------------------------------
# Per-node receipt — any Haystack component
# ---------------------------------------------------------------------------


class HaystackNodeReceiptV1(_ReceiptBase):
    """Per-component receipt for any node in a Haystack 2.x Pipeline."""

    schema_id: Literal["haystack_node_receipt/v1"] = "haystack_node_receipt/v1"
    node_name: str
    node_class: str
    input_hash: str
    output_hash: str
    latency_ms: float = Field(ge=0)
    upstream_nodes: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Editorial pipeline review — Art. 50(4)
# ---------------------------------------------------------------------------


class EditorialPipelineReviewV1(_ReceiptBase):
    """Article 50(4) — editorial / public-interest text review attestation."""

    schema_id: Literal["editorial_pipeline_review/v1"] = "editorial_pipeline_review/v1"
    article_subject_hash: str
    public_interest_category: Literal[
        "news",
        "current_affairs",
        "scientific",
        "policy",
        "legal_commentary",
        "civic_information",
        "other",
    ]
    human_editorial_review: bool
    reviewer_id: Optional[str] = None
    review_decision: Literal["published", "revised", "rejected", "pending"]
    pipeline_name: str
    generation_hash: str

    @model_validator(mode="after")
    def _reviewer_required_if_reviewed(self) -> "EditorialPipelineReviewV1":
        if self.human_editorial_review and not self.reviewer_id:
            raise ValueError(
                "reviewer_id is required when human_editorial_review=True (Art. 50(4))"
            )
        return self


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

SCHEMAS: dict[str, type[_ReceiptBase]] = {
    "rag_pipeline_session/v1": RagPipelineSessionV1,
    "generated_content/v1": GeneratedContentV1,
    "haystack_node_receipt/v1": HaystackNodeReceiptV1,
    "editorial_pipeline_review/v1": EditorialPipelineReviewV1,
}


def get_schema(schema_id: str) -> type[_ReceiptBase]:
    if schema_id not in SCHEMAS:
        raise KeyError(f"Unknown LedgerProof Haystack schema: {schema_id}")
    return SCHEMAS[schema_id]


def build_receipt(schema_id: str, **fields: Any) -> _ReceiptBase:
    """Validate and construct a receipt for the given schema."""
    cls = get_schema(schema_id)
    return cls(**fields)
