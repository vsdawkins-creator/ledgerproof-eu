"""
Receipt schemas for IBM watsonx.ai invocations under EU AI Act Article 50.

watsonx.ai is IBM's managed inference platform with EU-DE (Frankfurt) regional
deployment, project-and-tenant scoped access, and broad model support including
IBM's open-weights Granite family alongside Meta Llama, Mistral, and others.

The schema set captures what IBM enterprise buyers need:

  - chatbot_session/v1 — Article 50(1), direct chat interactions
  - generated_content/v1 — Article 50(2), synthetic content generation
  - eu_data_residency/v1 — Article 50(1) variant for watsonx.ai EU regions
    (eu-de, eu-gb). Records: attested region, watsonx project_id, IBM Cloud
    account / tenant attribution, cross-border transfer flag, SCC posture.
    Critical for German enterprise data residency obligations.
  - granite_open_model/v1 — Article 50(1) variant specifically for IBM Granite
    open-weights models. Records that the underlying weights are Apache-2.0
    licensed and reproducible, which materially changes the deployer's Article
    50 disclosure posture (open-weights provenance is auditable in a way that
    closed-weights APIs are not).

GDPR guardrail (heavy — IBM enterprise care):
  - Receipts MUST NOT contain raw prompt or response text by default.
  - Content is referenced via SHA-256 hashes only.
  - Free-text fields are length-bounded.
  - IBM Cloud CRN identifiers are accepted in the identifier regex (colons,
    slashes permitted).
  - `project_id` and `space_id` are normalized to UUID/identifier shapes.
  - Personal data fields are explicitly rejected at the schema layer.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

SchemaName = Literal[
    "chatbot_session/v1",
    "generated_content/v1",
    "eu_data_residency/v1",
    "granite_open_model/v1",
]

# watsonx.ai model IDs and IBM Cloud CRNs use a fairly wide character set:
#   ibm/granite-3-8b-instruct
#   meta-llama/llama-3-1-70b-instruct
#   crn:v1:bluemix:public:pm-20:eu-de:a/<acc>:<inst>::
_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:\-/+@]{1,256}$")

# UUID-ish project/space ID pattern. watsonx project IDs are UUIDs.
_UUID_LOOSE = re.compile(r"^[A-Za-z0-9\-]{8,64}$")

# Known watsonx model-ID prefixes → upstream-provider attribution.
# Structural classification only; LedgerProof does not endorse any provider.
_PROVIDER_PREFIXES = {
    "ibm": "ibm",
    "meta-llama": "meta",
    "mistralai": "mistral",
    "google": "google",
    "core42": "core42",
    "elyza": "elyza",
    "sdaia": "sdaia",
}

# IBM Granite open-weights model ID prefixes.
# Granite 3.x family is Apache-2.0 licensed and published on Hugging Face.
_GRANITE_PREFIXES = (
    "ibm/granite-3-",
    "ibm/granite-3.",
    "ibm/granite-13b-",
    "ibm/granite-20b-",
    "ibm/granite-7b-",
    "ibm/granite-8b-",
)

# EU regions for watsonx.ai data-residency schema.
# As of 2026, watsonx.ai is deployed in:
#   - eu-de (Frankfurt) — primary EU region, German enterprise focus
#   - eu-gb (London) — UK / post-Brexit, NOT EEA but often grouped
#   - us-south (Dallas), us-east, jp-tok, au-syd, ca-tor — non-EU
# For Article 50 + GDPR, only eu-de is unambiguously inside the EEA today.
EU_WATSONX_REGIONS = frozenset({"eu-de"})
EEA_AND_ADJACENT_REGIONS = frozenset({"eu-de", "eu-gb"})


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def infer_provider(model_id: str) -> str:
    """Best-effort: pull the upstream provider from a watsonx model_id."""
    if not model_id:
        return "unknown"
    head = model_id.split("/", 1)[0].lower()
    if head.startswith("crn:"):
        for prefix, name in _PROVIDER_PREFIXES.items():
            if f"/{prefix}/" in model_id.lower() or f":{prefix}/" in model_id.lower():
                return name
        return "unknown"
    return _PROVIDER_PREFIXES.get(head, "unknown")


def is_granite_open_model(model_id: str) -> bool:
    """True if the watsonx model_id is an IBM Granite open-weights model."""
    if not model_id:
        return False
    lowered = model_id.lower()
    return any(lowered.startswith(p) for p in _GRANITE_PREFIXES)


def is_eu_region(region: str | None) -> bool:
    """Strict EU/EEA check — eu-de only. eu-gb is NOT EEA post-Brexit."""
    return bool(region) and region.lower() in EU_WATSONX_REGIONS


def is_eea_or_adjacent(region: str | None) -> bool:
    """Looser check — includes UK (eu-gb) for deployers grouping UK with EU."""
    return bool(region) and region.lower() in EEA_AND_ADJACENT_REGIONS


def region_from_watsonx_url(url: str | None) -> str | None:
    """
    Extract the IBM Cloud region segment from a watsonx URL.

    Examples:
      https://eu-de.ml.cloud.ibm.com → "eu-de"
      https://us-south.ml.cloud.ibm.com → "us-south"
    """
    if not url:
        return None
    m = re.match(r"^https?://([A-Za-z0-9\-]+)\.ml\.cloud\.ibm\.com", url)
    if not m:
        return None
    return m.group(1).lower()


class _Base(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=False,
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class ModelRef(_Base):
    """Reference to the AI system used (watsonx.ai-side)."""

    provider: Annotated[str, StringConstraints(min_length=1, max_length=32)] = "watsonx"
    upstream_provider: Annotated[str, StringConstraints(min_length=1, max_length=32)] = "unknown"
    model_id: Annotated[str, StringConstraints(min_length=1, max_length=256)]
    response_id: Annotated[str, StringConstraints(min_length=1, max_length=256)]
    region: Annotated[str, StringConstraints(min_length=1, max_length=32)] | None = None
    project_id: Annotated[str, StringConstraints(min_length=1, max_length=64)] | None = None
    space_id: Annotated[str, StringConstraints(min_length=1, max_length=64)] | None = None
    deployment_id: Annotated[str, StringConstraints(min_length=1, max_length=64)] | None = None
    stop_reason: Annotated[str, StringConstraints(max_length=64)] | None = None
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    is_open_weights: bool = False

    @field_validator("project_id", "space_id", "deployment_id")
    @classmethod
    def _validate_uuidish(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not _UUID_LOOSE.match(v):
            raise ValueError(
                f"watsonx project/space/deployment id {v!r} is not in expected shape"
            )
        return v


class ContentRef(_Base):
    """SHA-256 reference to message content. Raw text NEVER stored in receipts."""

    sha256_hex: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    byte_length: int = Field(ge=0)
    role: Literal["user", "assistant", "system", "tool"]


class ToolUseRef(_Base):
    """Tool call binding for agent-style receipts."""

    tool_name: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    tool_use_id: Annotated[str, StringConstraints(min_length=1, max_length=256)]
    input_sha256_hex: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    output_sha256_hex: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")] | None = None


class RegulatoryContext(_Base):
    """Deployer-supplied regulatory metadata."""

    article_50_paragraph: Literal["1", "2", "3", "4"]
    deployer_jurisdiction: Annotated[str, StringConstraints(min_length=2, max_length=8)]
    end_user_disclosure_made: bool
    notes: Annotated[str, StringConstraints(max_length=512)] | None = None


class DataResidencyAttestation(_Base):
    """
    Self-attestation by the deployer that the watsonx.ai call ran in an EU region.

    LedgerProof does NOT verify this against IBM Cloud; it records the
    deployer's own attestation alongside the region pulled from the
    `Credentials.url`. The verifier compares `attested_region` with
    `model.region` to catch drift.

    GDPR-heavy fields: `tenant_id` (IBM Cloud account hash, NOT raw account),
    `sccs_in_place`, `cross_border_transfer`.
    """

    attested_region: Annotated[str, StringConstraints(min_length=2, max_length=32)]
    eu_region: bool
    cross_border_transfer: bool = False
    sccs_in_place: bool | None = None  # Standard Contractual Clauses
    tenant_id: Annotated[str, StringConstraints(max_length=128)] | None = None
    notes: Annotated[str, StringConstraints(max_length=512)] | None = None

    @field_validator("attested_region")
    @classmethod
    def _normalize_region(cls, v: str) -> str:
        return v.strip().lower()


class OpenWeightsAttestation(_Base):
    """
    Self-attestation for an IBM Granite open-weights call.

    Granite 3.x is Apache-2.0 licensed and the weights are published on
    Hugging Face. This attestation records the deployer's claim that the
    underlying weights are reproducible, which materially strengthens the
    Article 50 disclosure (open-weights provenance is auditable in a way
    that closed-weights APIs are not).
    """

    model_family: Annotated[str, StringConstraints(min_length=1, max_length=64)] = "ibm-granite"
    license_spdx: Annotated[str, StringConstraints(min_length=1, max_length=64)] = "Apache-2.0"
    weights_url: Annotated[str, StringConstraints(max_length=512)] | None = None
    reproducible: bool = True
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
    streaming: bool = False
    residency: DataResidencyAttestation | None = None
    open_weights: OpenWeightsAttestation | None = None
    adapter: Annotated[str, StringConstraints(max_length=64)] = "ledgerproof-watsonx"
    adapter_version: Annotated[str, StringConstraints(max_length=32)] = "0.1.0"

    @field_validator("deployer_id", "receipt_id")
    @classmethod
    def _validate_id(cls, v: str) -> str:
        if not _ID_PATTERN.match(v):
            raise ValueError(
                f"identifier {v!r} contains disallowed characters; "
                "use only [A-Za-z0-9._:-/+@] up to 256 chars"
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


def build_eu_residency_receipt(**kwargs: Any) -> ReceiptV1:
    return ReceiptV1(schema="eu_data_residency/v1", **kwargs)


def build_granite_open_model_receipt(**kwargs: Any) -> ReceiptV1:
    return ReceiptV1(schema="granite_open_model/v1", **kwargs)
