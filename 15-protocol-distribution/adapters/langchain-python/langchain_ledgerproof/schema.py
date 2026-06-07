"""Pydantic v2 schemas for LedgerProof transparency receipts.

Three schema variants, one per EU AI Act Article 50 disclosure obligation:

  * chatbot_session/v1    -> Article 50(1)  AI-system-interaction disclosure
  * generated_content/v1  -> Article 50(2)  AI-generated content marking
  * human_review/v1       -> Article 50(4)  editorial-control exemption

GDPR safety: the validators on `deployer_id`, `reviewer_role`, and
`review_rationale` reject email-shaped strings. These fields should hold
opaque pseudonymous identifiers, not personal data.
"""

from __future__ import annotations

import re
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

# Conservative email pattern. We are not trying to do RFC 5322 — we are
# trying to catch the obvious "alice@corp.example" case so it never lands
# in a receipt by accident.
_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def _reject_email_shaped(value: str, field_name: str) -> str:
    if _EMAIL_RE.match(value.strip()):
        raise ValueError(
            f"GDPR safety: {field_name!r} appears to be an email address. "
            "Use a pseudonymous identifier instead."
        )
    return value


class _BaseReceipt(BaseModel):
    """Common header fields for all receipt variants."""

    schema_id: str = Field(..., description="Receipt schema, e.g. 'chatbot_session/v1'")
    run_id: str = Field(..., description="Unique run identifier (UUID string)")
    timestamp_utc: str = Field(..., description="ISO-8601 UTC timestamp")
    deployer_id: str = Field(
        ...,
        description="Pseudonymous deployer identifier. MUST NOT be an email.",
        min_length=1,
        max_length=256,
    )
    transcript_sha256: str = Field(
        ...,
        description="Hex-encoded SHA-256 of the canonicalized transcript",
        pattern=r"^[0-9a-f]{64}$",
    )

    @field_validator("deployer_id")
    @classmethod
    def _check_deployer(cls, v: str) -> str:
        return _reject_email_shaped(v, "deployer_id")


class ChatbotSessionReceipt(_BaseReceipt):
    """Article 50(1): the user was interacting with an AI system."""

    schema_id: Literal["chatbot_session/v1"] = "chatbot_session/v1"
    model_identifier: str = Field(..., description="Model name/version (e.g. 'gpt-4o-mini')")
    disclosure_shown: bool = Field(
        True, description="Whether AI-interaction disclosure was shown to the user"
    )


class GeneratedContentReceipt(_BaseReceipt):
    """Article 50(2): the content was generated or substantially modified by AI."""

    schema_id: Literal["generated_content/v1"] = "generated_content/v1"
    model_identifier: str
    content_type: str = Field(..., description="MIME-ish content type, e.g. 'text/markdown'")
    machine_readable_mark: bool = Field(
        True,
        description="True if the output carries a machine-readable provenance mark",
    )


class HumanReviewReceipt(_BaseReceipt):
    """Article 50(4): editorial control exemption — content human-reviewed before publication."""

    schema_id: Literal["human_review/v1"] = "human_review/v1"
    reviewer_id: str = Field(..., description="Pseudonymous reviewer identifier")
    reviewer_role: str = Field(..., description="Role (e.g. 'editor', 'compliance'). NOT an email.")
    review_rationale: Optional[str] = Field(
        None,
        description="Free-text rationale. NOT an email. Keep terse to avoid PII leakage.",
        max_length=2000,
    )
    review_outcome: Literal["approved", "rejected", "modified"] = "approved"

    @field_validator("reviewer_id")
    @classmethod
    def _check_reviewer_id(cls, v: str) -> str:
        return _reject_email_shaped(v, "reviewer_id")

    @field_validator("reviewer_role")
    @classmethod
    def _check_reviewer_role(cls, v: str) -> str:
        return _reject_email_shaped(v, "reviewer_role")

    @field_validator("review_rationale")
    @classmethod
    def _check_rationale(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return _reject_email_shaped(v, "review_rationale")


SCHEMAS: dict[str, type[_BaseReceipt]] = {
    "chatbot_session/v1": ChatbotSessionReceipt,
    "generated_content/v1": GeneratedContentReceipt,
    "human_review/v1": HumanReviewReceipt,
}


def get_schema(schema_id: str) -> type[_BaseReceipt]:
    """Look up a schema class by its identifier."""
    try:
        return SCHEMAS[schema_id]
    except KeyError as exc:
        raise ValueError(
            f"Unknown receipt schema: {schema_id!r}. Known: {sorted(SCHEMAS)}"
        ) from exc
