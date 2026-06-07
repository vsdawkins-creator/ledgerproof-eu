"""Receipt schemas for LedgerProof-Snowflake-Cortex.

Each schema is a versioned Pydantic model that, once validated, becomes the
canonical body of a transparency receipt. GDPR validators enforce that only
hashed or pseudonymous identifiers reach a receipt — never raw personal data.

The Snowflake-specific schemas (`enterprise_data_lineage/v1` and
`cortex_search_rag/v1`) capture warehouse-side source attribution so a
synthetic-content or RAG flow grounded in Snowflake data can be audited
back to the governed dataset that produced it — without leaking the rows
themselves.
"""

from __future__ import annotations

import hashlib
import re
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class ReceiptSchemaName(str, Enum):
    CHATBOT_SESSION_V1 = "chatbot_session/v1"
    GENERATED_CONTENT_V1 = "generated_content/v1"
    ENTERPRISE_DATA_LINEAGE_V1 = "enterprise_data_lineage/v1"
    CORTEX_SEARCH_RAG_V1 = "cortex_search_rag/v1"


class GDPRValidationError(ValueError):
    """Raised when a field that should be hashed/pseudonymised contains
    apparently raw personal data."""


_HASH_PREFIX_RE = re.compile(r"^(sha256|sha3-256|blake2b):[0-9a-fA-F]{32,128}$")
_EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
# Conservative Snowflake-identifier check: unquoted identifiers are
# letters, digits, underscores, dollar signs; double-quoted identifiers
# are allowed but must not contain newline characters.
_SF_IDENT_RE = re.compile(r'^("[^"\r\n]+"|[A-Za-z_][A-Za-z0-9_$]*)$')
# Fully-qualified or partially-qualified table identifier
# (db.schema.table, schema.table, or table).
_SF_TABLE_RE = re.compile(
    r'^("[^"\r\n]+"|[A-Za-z_][A-Za-z0-9_$]*)'
    r'(\.("[^"\r\n]+"|[A-Za-z_][A-Za-z0-9_$]*)){0,2}$'
)


def validate_gdpr_safe(value: Optional[str], *, field_name: str) -> Optional[str]:
    """Reject obviously raw personal data in receipt identifier fields.

    Permits: None, empty string, or a prefixed hash like 'sha256:abc...'.
    Rejects: bare email addresses or long unhashed strings.
    """
    if value is None or value == "":
        return value
    if _HASH_PREFIX_RE.match(value):
        return value
    if _EMAIL_RE.search(value):
        raise GDPRValidationError(
            f"Field {field_name!r} appears to contain a raw email. "
            "Hash it first (e.g. 'sha256:<hex>')."
        )
    if len(value) > 64 and " " in value:
        raise GDPRValidationError(
            f"Field {field_name!r} looks like free-form personal data. "
            "Hash or pseudonymise before placing it in a receipt."
        )
    return value


def _validate_sf_identifier(value: Optional[str], *, field_name: str) -> Optional[str]:
    if value is None or value == "":
        return value
    if not _SF_IDENT_RE.match(value):
        raise ValueError(
            f"Field {field_name!r} ({value!r}) is not a valid Snowflake "
            "identifier."
        )
    return value


def _validate_sf_table(value: str, *, field_name: str) -> str:
    if not _SF_TABLE_RE.match(value):
        raise ValueError(
            f"Field {field_name!r} ({value!r}) is not a valid Snowflake "
            "table identifier (expected name, schema.name, or db.schema.name)."
        )
    return value


def hash_str(text: str, algo: str = "sha256") -> str:
    """Convenience helper to produce a GDPR-safe identifier."""
    h = hashlib.new(algo, text.encode("utf-8")).hexdigest()
    return f"{algo}:{h}"


class _ReceiptBase(BaseModel):
    schema_name: ReceiptSchemaName
    model: str = Field(..., description="Snowflake Cortex model identifier")
    provider: str = Field(default="snowflake-cortex")
    timestamp_unix_ms: int = Field(..., description="Receipt creation time, ms since epoch")
    deployer_id: str = Field(..., description="Deployer identifier (Article 3(4))")

    model_config = {"extra": "forbid"}


class ChatbotSessionV1(_ReceiptBase):
    """Article 50(1) — natural-person interaction with an AI chatbot."""

    schema_name: ReceiptSchemaName = ReceiptSchemaName.CHATBOT_SESSION_V1
    subject_id_hash: Optional[str] = Field(
        default=None,
        description="Pseudonymous identifier for the natural person (hashed).",
    )
    session_id_hash: Optional[str] = None
    prompt_hash: Optional[str] = None
    completion_hash: Optional[str] = None
    disclosure_shown: bool = Field(
        default=False,
        description="Whether the Article 50(1) AI-interaction disclosure was shown.",
    )

    @field_validator("subject_id_hash", "session_id_hash", "prompt_hash", "completion_hash")
    @classmethod
    def _gdpr(cls, v, info):
        return validate_gdpr_safe(v, field_name=info.field_name)


class GeneratedContentV1(_ReceiptBase):
    """Article 50(2) — synthetic content marking."""

    schema_name: ReceiptSchemaName = ReceiptSchemaName.GENERATED_CONTENT_V1
    content_hash: str = Field(..., description="Hash of the generated artefact.")
    content_type: str = Field(default="text", description="text | audio | image | video")
    marking_method: Optional[str] = Field(
        default=None, description="e.g. 'visible-label', 'c2pa', 'watermark'"
    )

    @field_validator("content_hash")
    @classmethod
    def _hash_required(cls, v):
        if not _HASH_PREFIX_RE.match(v):
            raise GDPRValidationError(
                "content_hash must be a prefixed hash, e.g. 'sha256:<hex>'."
            )
        return v


class EnterpriseDataLineageV1(_ReceiptBase):
    """Article 50(2) variant with Snowflake warehouse + database + schema +
    table-source attribution.

    Captures *which governed dataset* produced the synthetic content so a
    regulator-facing audit can reconstruct the data-lineage path without
    surfacing the underlying rows. Identifiers only; no row content.
    """

    schema_name: ReceiptSchemaName = ReceiptSchemaName.ENTERPRISE_DATA_LINEAGE_V1
    content_hash: str = Field(..., description="Hash of the generated artefact.")
    content_type: str = Field(default="text", description="text | audio | image | video")
    marking_method: Optional[str] = Field(default=None)
    warehouse: Optional[str] = Field(
        default=None,
        description="Snowflake virtual warehouse used (e.g. 'COMPUTE_WH').",
    )
    source_database: Optional[str] = Field(
        default=None, description="Source database identifier."
    )
    source_schema: Optional[str] = Field(
        default=None, description="Source schema identifier."
    )
    source_tables: List[str] = Field(
        default_factory=list,
        description="Source table identifiers (unqualified, schema.name, or db.schema.name).",
    )
    query_id: Optional[str] = Field(
        default=None,
        description="Snowflake query id of the generating query, if known.",
    )
    role: Optional[str] = Field(
        default=None, description="Snowflake role under which inference ran."
    )

    @field_validator("content_hash")
    @classmethod
    def _hash_required(cls, v):
        if not _HASH_PREFIX_RE.match(v):
            raise GDPRValidationError(
                "content_hash must be a prefixed hash, e.g. 'sha256:<hex>'."
            )
        return v

    @field_validator("warehouse", "source_database", "source_schema", "role")
    @classmethod
    def _ident(cls, v, info):
        return _validate_sf_identifier(v, field_name=info.field_name)

    @field_validator("source_tables")
    @classmethod
    def _tables(cls, v):
        return [_validate_sf_table(t, field_name="source_tables") for t in v]


class CortexSearchRagV1(_ReceiptBase):
    """Article 50(1) variant for chatbot answers grounded in a Cortex Search
    Service RAG flow.

    Captures the Search Service identifier and the hashed retrieval
    fingerprint so a regulator-facing audit can reconstruct *which* governed
    corpus produced a given answer, without exposing the retrieved rows.
    """

    schema_name: ReceiptSchemaName = ReceiptSchemaName.CORTEX_SEARCH_RAG_V1
    subject_id_hash: Optional[str] = None
    session_id_hash: Optional[str] = None
    query_hash: Optional[str] = None
    completion_hash: Optional[str] = None
    disclosure_shown: bool = Field(default=False)
    search_service_name: str = Field(
        ...,
        description="Fully-qualified Cortex Search Service name (db.schema.name).",
    )
    retrieved_doc_count: int = Field(default=0, ge=0)
    retrieval_fingerprint_hash: Optional[str] = Field(
        default=None,
        description="Hash over the concatenated retrieved-document identifiers.",
    )
    columns_returned: List[str] = Field(default_factory=list)

    @field_validator(
        "subject_id_hash", "session_id_hash", "query_hash",
        "completion_hash", "retrieval_fingerprint_hash",
    )
    @classmethod
    def _gdpr(cls, v, info):
        return validate_gdpr_safe(v, field_name=info.field_name)

    @field_validator("search_service_name")
    @classmethod
    def _service(cls, v):
        return _validate_sf_table(v, field_name="search_service_name")


SCHEMA_REGISTRY = {
    ReceiptSchemaName.CHATBOT_SESSION_V1: ChatbotSessionV1,
    ReceiptSchemaName.GENERATED_CONTENT_V1: GeneratedContentV1,
    ReceiptSchemaName.ENTERPRISE_DATA_LINEAGE_V1: EnterpriseDataLineageV1,
    ReceiptSchemaName.CORTEX_SEARCH_RAG_V1: CortexSearchRagV1,
}


def resolve_schema(name: str | ReceiptSchemaName) -> type[_ReceiptBase]:
    if isinstance(name, str):
        name = ReceiptSchemaName(name)
    return SCHEMA_REGISTRY[name]
