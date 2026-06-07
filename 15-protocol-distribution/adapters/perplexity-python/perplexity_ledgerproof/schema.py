"""Receipt schemas — Pydantic v2.

Four schemas tailored to Perplexity AI deployment surfaces. Perplexity's
distinctive feature is **live web search with citations**: every Sonar model
response includes a `citations` field (list of source URLs) that grounded
the assistant answer. That makes Perplexity uniquely well-suited to
Article 50(4) — labelling AI-generated text "disseminated to the public on
matters of public interest" — because the citation provenance is part of
the response surface, not an afterthought.

Schemas:

- `chatbot_session/v1`             — Article 50(1): natural person interacting
                                      with an AI system
- `generated_content/v1`           — Article 50(2): synthetically generated or
                                      manipulated content
- `ai_search_with_citations/v1`    — Article 50(1)+(4) variant: Perplexity's
                                      live search + citation surface. Binds the
                                      receipt to (prompt hash, citation-list
                                      hash, response hash) so an auditor can
                                      verify *which* sources the answer drew on.
- `public_interest_text/v1`        — Article 50(4) specifically: AI-generated
                                      text disseminated to inform the public on
                                      matters of public interest (news,
                                      civic discourse, public health, etc.),
                                      with citation provenance.

GDPR discipline: receipts MUST NOT carry plaintext PII. We store hashes of
prompt/response, never raw text. The `user_pseudonym` field MUST be a hash,
opaque ID, or empty — validators reject anything that looks like a raw email
address.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


_EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class _ReceiptBase(BaseModel):
    """Common fields across all receipt schemas."""

    schema_id: str
    timestamp: str = Field(default_factory=_utc_now_iso)
    deployer_id: str
    model_provider: Literal["perplexity"] = "perplexity"
    model_id: str
    interaction_id: str
    prompt_sha256: str
    response_sha256: str
    user_pseudonym: str | None = None
    jurisdiction: str = "EU"
    extra: dict[str, Any] = Field(default_factory=dict)

    @field_validator("user_pseudonym")
    @classmethod
    def _no_raw_pii(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return v
        if _EMAIL_RE.search(v):
            raise ValueError(
                "user_pseudonym must not contain raw email addresses. "
                "Hash or pseudonymize first (GDPR Art. 5(1)(c) — data minimization)."
            )
        return v

    @field_validator("prompt_sha256", "response_sha256")
    @classmethod
    def _is_hex_sha256(cls, v: str) -> str:
        if len(v) != 64 or any(c not in "0123456789abcdef" for c in v.lower()):
            raise ValueError("must be a 64-char lowercase hex SHA-256")
        return v.lower()

    @field_validator("deployer_id")
    @classmethod
    def _is_urn(cls, v: str) -> str:
        if not v.startswith("urn:"):
            raise ValueError(
                "deployer_id should be a URN (e.g. 'urn:eu:deployer:acme')"
            )
        return v


class ChatbotSessionV1(_ReceiptBase):
    """Article 50(1): a natural person is interacting with an AI system."""

    schema_id: Literal["chatbot_session/v1"] = "chatbot_session/v1"
    article_basis: Literal["EU_AI_Act_Art_50_1"] = "EU_AI_Act_Art_50_1"
    disclosure_shown: bool = False


class GeneratedContentV1(_ReceiptBase):
    """Article 50(2): synthetically generated audio/image/video/text content."""

    schema_id: Literal["generated_content/v1"] = "generated_content/v1"
    article_basis: Literal["EU_AI_Act_Art_50_2"] = "EU_AI_Act_Art_50_2"
    content_modality: Literal["text", "image", "audio", "video"] = "text"
    machine_readable_marker: bool = True


class AISearchWithCitationsV1(_ReceiptBase):
    """Article 50(1)+(4) variant — Perplexity's AI search with citation surface.

    Captures the binding between:
      - the user's search query (`prompt_sha256`),
      - the citation URLs returned by Perplexity (`citations_sha256` and
        `citations_count`),
      - the assistant response (`response_sha256`).

    `citations_sha256` is computed by `canonical.citation_list_hash_hex()` —
    a deterministic SHA-256 over the lex-sorted, canonical-CBOR-encoded URL
    list. The adapter does NOT fetch or validate URLs (constraint C4 — local
    verification only). The deployer is responsible for preserving the
    citation list alongside the receipt so an auditor can independently
    re-compute the hash.

    Strategic for Article 50(4): a regulator inquiry into AI-generated text
    disseminated to inform the public can be answered with a single signed
    receipt that proves *which* prompt produced *which* answer using *which*
    citations, plus an Bitcoin-anchored timestamp.
    """

    schema_id: Literal["ai_search_with_citations/v1"] = "ai_search_with_citations/v1"
    article_basis: Literal["EU_AI_Act_Art_50_1"] = "EU_AI_Act_Art_50_1"
    citations_sha256: str | None = None
    citations_count: int = 0
    search_used: bool = True

    @field_validator("citations_sha256")
    @classmethod
    def _maybe_hex_sha256(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        if len(v) != 64 or any(c not in "0123456789abcdef" for c in v.lower()):
            raise ValueError(
                "citations_sha256 must be 64-char lowercase hex SHA-256"
            )
        return v.lower()

    @field_validator("citations_count")
    @classmethod
    def _non_negative_count(cls, v: int) -> int:
        if v < 0:
            raise ValueError("citations_count must be >= 0")
        return v


class PublicInterestTextV1(_ReceiptBase):
    """Article 50(4) specifically — AI-generated/manipulated text disseminated
    to inform the public on matters of public interest, with citation
    provenance.

    Fields beyond the base capture the public-interest-text disclosure surface:
      - `disclosure_label_shown` — did the deployer surface the AI-generated
        disclosure label to the end user? (Art. 50(4) obligation.)
      - `editorial_review` — was the output reviewed by a human editor before
        publication? (Art. 50(4) carve-out: obligation reduces where the AI
        output undergoes human review and a person/entity holds editorial
        responsibility for publication.)
      - `citations_sha256` / `citations_count` — same canonical citation hash
        as in `AISearchWithCitationsV1`; binds the receipt to the source
        attribution surface that Perplexity returned alongside the answer.
      - `subject_category` — free-form deployer string (e.g. `"news.politics"`,
        `"health.public_health"`, `"civic"`); not validated, used for filtering
        in receipt-warehouse queries.
    """

    schema_id: Literal["public_interest_text/v1"] = "public_interest_text/v1"
    article_basis: Literal["EU_AI_Act_Art_50_4"] = "EU_AI_Act_Art_50_4"
    content_modality: Literal["text"] = "text"
    disclosure_label_shown: bool = False
    editorial_review: bool = False
    citations_sha256: str | None = None
    citations_count: int = 0
    subject_category: str | None = None

    @field_validator("citations_sha256")
    @classmethod
    def _maybe_hex_sha256(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        if len(v) != 64 or any(c not in "0123456789abcdef" for c in v.lower()):
            raise ValueError(
                "citations_sha256 must be 64-char lowercase hex SHA-256"
            )
        return v.lower()

    @field_validator("citations_count")
    @classmethod
    def _non_negative_count(cls, v: int) -> int:
        if v < 0:
            raise ValueError("citations_count must be >= 0")
        return v


SCHEMAS = {
    "chatbot_session/v1": ChatbotSessionV1,
    "generated_content/v1": GeneratedContentV1,
    "ai_search_with_citations/v1": AISearchWithCitationsV1,
    "public_interest_text/v1": PublicInterestTextV1,
}


def build_receipt(schema_id: str, **fields: Any) -> _ReceiptBase:
    """Construct a receipt by schema_id."""
    cls = SCHEMAS.get(schema_id)
    if cls is None:
        raise ValueError(
            f"Unknown schema_id={schema_id!r}. Known: {list(SCHEMAS)}"
        )
    return cls(**fields)
