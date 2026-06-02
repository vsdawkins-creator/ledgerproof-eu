"""Pydantic schemas for LedgerProof Vertex AI receipts.

Schemas:
- chatbot_session/v1          (Article 50(1))
- generated_content/v1        (Article 50(2))
- eu_data_residency/v1        (Article 50(1) variant — captures project,
                               location, and region-of-inference attestation)
- gemini_function_call/v1     (internal audit, tool invocations)

GDPR note (deployer_id validator): deployer_id MUST NOT contain unhashed
PII (no @, no naive email patterns). It SHOULD be a URN or opaque deployer
identifier.
"""
from __future__ import annotations

import re
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


SCHEMA_NAMES = (
    "chatbot_session/v1",
    "generated_content/v1",
    "eu_data_residency/v1",
    "gemini_function_call/v1",
)


# Reject obvious PII patterns (email, full names with whitespace, etc.).
_PII_RE = re.compile(r"@|\s")


def _validate_deployer_id(v: str) -> str:
    if not v:
        raise ValueError("deployer_id is required")
    if len(v) > 256:
        raise ValueError("deployer_id too long (max 256)")
    if _PII_RE.search(v):
        raise ValueError(
            "deployer_id appears to contain PII (whitespace or '@'). "
            "Use a URN such as 'urn:lpr:deployer:<opaque>' (GDPR Art. 5(1)(c))."
        )
    return v


class VertexContext(BaseModel):
    """Vertex AI deployment context — captured for every receipt."""

    project: str | None = None
    location: str | None = None
    model: str
    # Region attestation: free-form short label describing the *configured*
    # region of inference. For europe-west4 → "EU/NL".
    region_of_inference_attestation: str | None = None


class _BaseReceipt(BaseModel):
    protocol: Literal["lpr/0.1"] = "lpr/0.1"
    schema_name: str = Field(..., alias="schema")
    deployer_id: str
    occurred_at: str  # RFC 3339 / ISO 8601 UTC
    vertex: VertexContext

    model_config = {"populate_by_name": True}

    @field_validator("deployer_id")
    @classmethod
    def _v_deployer(cls, v: str) -> str:
        return _validate_deployer_id(v)


class ChatbotSessionReceipt(_BaseReceipt):
    schema_name: Literal["chatbot_session/v1"] = Field(
        "chatbot_session/v1", alias="schema"
    )
    session_id: str
    turn_index: int
    input_digest: str  # hex SHA-256 of input
    output_digest: str  # hex SHA-256 of output
    article_50_paragraph: Literal["50(1)"] = "50(1)"


class GeneratedContentReceipt(_BaseReceipt):
    schema_name: Literal["generated_content/v1"] = Field(
        "generated_content/v1", alias="schema"
    )
    content_type: str = "text"  # text | code | image | audio | video
    input_digest: str
    output_digest: str
    article_50_paragraph: Literal["50(2)"] = "50(2)"


class EuDataResidencyReceipt(_BaseReceipt):
    """Strategic schema for European compliance audits.

    Asserts the *configured* Vertex AI project + location + region-of-
    inference attestation alongside the standard input/output digests.
    Note: this attests *deployer configuration*, not Google Cloud's
    physical routing — see README C1 disclaimer.
    """

    schema_name: Literal["eu_data_residency/v1"] = Field(
        "eu_data_residency/v1", alias="schema"
    )
    input_digest: str
    output_digest: str
    gdpr_lawful_basis_hint: str | None = None  # opaque, deployer-supplied
    article_50_paragraph: Literal["50(1)"] = "50(1)"


class GeminiFunctionCallReceipt(_BaseReceipt):
    schema_name: Literal["gemini_function_call/v1"] = Field(
        "gemini_function_call/v1", alias="schema"
    )
    function_name: str
    arguments_digest: str
    article_50_paragraph: Literal["50(1)"] = "50(1)"


def build_receipt_payload(
    schema_name: str,
    deployer_id: str,
    occurred_at: str,
    vertex: VertexContext,
    **fields: Any,
) -> dict[str, Any]:
    """Construct + validate a receipt payload dict for a given schema."""
    if schema_name == "chatbot_session/v1":
        m = ChatbotSessionReceipt(
            schema=schema_name,
            deployer_id=deployer_id,
            occurred_at=occurred_at,
            vertex=vertex,
            **fields,
        )
    elif schema_name == "generated_content/v1":
        m = GeneratedContentReceipt(
            schema=schema_name,
            deployer_id=deployer_id,
            occurred_at=occurred_at,
            vertex=vertex,
            **fields,
        )
    elif schema_name == "eu_data_residency/v1":
        m = EuDataResidencyReceipt(
            schema=schema_name,
            deployer_id=deployer_id,
            occurred_at=occurred_at,
            vertex=vertex,
            **fields,
        )
    elif schema_name == "gemini_function_call/v1":
        m = GeminiFunctionCallReceipt(
            schema=schema_name,
            deployer_id=deployer_id,
            occurred_at=occurred_at,
            vertex=vertex,
            **fields,
        )
    else:
        raise ValueError(
            f"Unknown schema: {schema_name!r}. Known: {SCHEMA_NAMES}"
        )
    return m.model_dump(by_alias=True, exclude_none=True)
