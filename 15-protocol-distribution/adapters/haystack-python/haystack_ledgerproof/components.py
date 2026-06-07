"""LedgerProofComponent — a Haystack 2.x @component for receipt emission.

Drop this into any Haystack Pipeline; connect upstream output(s) to its
input socket and receive a signed, side-channel receipt for every run.

C7: emission is side-channel; the input flows through unchanged on the
"passthrough" output socket so downstream nodes are unaffected.
"""

from __future__ import annotations

import base64
import time
import uuid
from typing import Any, Optional

from .canonical import canonical_cbor, hash_payload, sha256_hex
from .emitter import Emitter, MemoryEmitter
from .schema import build_receipt
from .signer import SigningKey

# Haystack's `@component` decorator may or may not be importable in test
# environments. We try the real import; if unavailable, fall back to a
# noop decorator so this module remains importable for documentation and
# for unit tests that don't exercise pipeline wiring.
try:
    from haystack import component
    from haystack.dataclasses import ChatMessage  # type: ignore[attr-defined]

    _HAYSTACK_AVAILABLE = True
except Exception:  # pragma: no cover - exercised only when haystack missing
    _HAYSTACK_AVAILABLE = False

    def component(cls):  # type: ignore[no-redef]
        return cls

    ChatMessage = None  # type: ignore[assignment, misc]


def _coerce_text(value: Any) -> str:
    """Best-effort string projection for hashing arbitrary Haystack values."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, list):
        return "\n".join(_coerce_text(v) for v in value)
    if ChatMessage is not None and isinstance(value, ChatMessage):
        return getattr(value, "content", "") or getattr(value, "text", "") or ""
    # objects with .content / .text
    for attr in ("content", "text", "answer"):
        if hasattr(value, attr):
            inner = getattr(value, attr)
            if inner is not None:
                return _coerce_text(inner)
    return str(value)


@component
class LedgerProofComponent:
    """Side-channel LedgerProof receipt component.

    Args:
        signing_key: Ed25519 SigningKey used to sign each receipt.
        schema: One of the LedgerProof schema ids (see `schema.SCHEMAS`).
        deployer: Stable deployer identifier (Art. 50 attribution).
        emitter: Sink for signed envelopes; defaults to in-memory.
        model_id: Model identifier (required for some schemas).
        node_name: Logical node label written into the receipt.
        gdpr_lawful_basis: Optional lawful basis (Art. 6 GDPR) to unlock
            PII-containing fields.
        extra_fields: Static extra fields merged into the receipt.
    """

    def __init__(
        self,
        signing_key: SigningKey,
        schema: str = "haystack_node_receipt/v1",
        deployer: str = "unspecified-deployer",
        emitter: Optional[Emitter] = None,
        model_id: str = "unspecified-model",
        node_name: str = "ledgerproof",
        gdpr_lawful_basis: Optional[str] = None,
        extra_fields: Optional[dict[str, Any]] = None,
    ):
        self.signing_key = signing_key
        self.schema = schema
        self.deployer = deployer
        self.emitter = emitter if emitter is not None else MemoryEmitter()
        self.model_id = model_id
        self.node_name = node_name
        self.gdpr_lawful_basis = gdpr_lawful_basis
        self.extra_fields = extra_fields or {}

    if _HAYSTACK_AVAILABLE:
        # Use the run-decorator form so Haystack registers output sockets.
        @component.output_types(receipt_id=str, signature_b64=str, content=Any)  # type: ignore[misc]
        def run(self, content: Any, query: Any = None) -> dict[str, Any]:
            return self._run_impl(content=content, query=query)
    else:
        def run(self, content: Any, query: Any = None) -> dict[str, Any]:  # type: ignore[no-redef]
            return self._run_impl(content=content, query=query)

    def _run_impl(self, content: Any, query: Any = None) -> dict[str, Any]:
        """Hash `content` (and optional `query`), sign, emit.

        Returns:
            dict with `receipt_id`, `signature_b64`, and a passthrough
            `content` socket for downstream nodes.
        """
        start = time.time()
        content_text = _coerce_text(content)
        query_text = _coerce_text(query) if query is not None else ""

        content_hash = sha256_hex(content_text)
        query_hash = sha256_hex(query_text) if query_text else sha256_hex(b"")

        fields = self._build_schema_fields(
            content_text=content_text,
            content_hash=content_hash,
            query_hash=query_hash,
            start=start,
        )
        fields.update(self.extra_fields)

        receipt = build_receipt(self.schema, **fields)
        payload = receipt.model_dump()
        signature = self.signing_key.sign(canonical_cbor(payload))

        envelope = {
            "receipt": payload,
            "signature_alg": "ed25519",
            "signature_b64": base64.b64encode(signature).decode("ascii"),
            "public_key_b64": self.signing_key.public_key_b64(),
        }
        self.emitter.emit(envelope)

        return {
            "receipt_id": payload["receipt_id"],
            "signature_b64": envelope["signature_b64"],
            "content": content,  # C7: passthrough, unmodified
        }

    # -- schema-specific field assembly --------------------------------------

    def _build_schema_fields(
        self,
        *,
        content_text: str,
        content_hash: str,
        query_hash: str,
        start: float,
    ) -> dict[str, Any]:
        base = {
            "receipt_id": str(uuid.uuid4()),
            "deployer": self.deployer,
            "key_id": self.signing_key.key_id,
            "gdpr_lawful_basis": self.gdpr_lawful_basis,
        }
        if self.schema == "generated_content/v1":
            base.update(
                content_type="text",
                content_hash=content_hash,
                content_length=len(content_text.encode("utf-8")),
                model_id=self.model_id,
                generator_class=self.extra_fields.get(
                    "generator_class", "HaystackGenerator"
                ),
            )
        elif self.schema == "rag_pipeline_session/v1":
            base.update(
                pipeline_name=self.extra_fields.get("pipeline_name", "haystack-pipeline"),
                pipeline_hash=self.extra_fields.get(
                    "pipeline_hash", sha256_hex(self.node_name)
                ),
                component_count=int(self.extra_fields.get("component_count", 1)),
                retrieved_doc_count=int(self.extra_fields.get("retrieved_doc_count", 0)),
                query_hash=query_hash,
                answer_hash=content_hash,
                model_id=self.model_id,
                user_facing_disclosure_shown=bool(
                    self.extra_fields.get("user_facing_disclosure_shown", True)
                ),
            )
        elif self.schema == "haystack_node_receipt/v1":
            base.update(
                node_name=self.node_name,
                node_class=self.extra_fields.get("node_class", "LedgerProofComponent"),
                input_hash=query_hash,
                output_hash=content_hash,
                latency_ms=round((time.time() - start) * 1000, 3),
                upstream_nodes=list(self.extra_fields.get("upstream_nodes", [])),
            )
        elif self.schema == "editorial_pipeline_review/v1":
            base.update(
                article_subject_hash=query_hash,
                public_interest_category=self.extra_fields.get(
                    "public_interest_category", "other"
                ),
                human_editorial_review=bool(
                    self.extra_fields.get("human_editorial_review", False)
                ),
                reviewer_id=self.extra_fields.get("reviewer_id"),
                review_decision=self.extra_fields.get("review_decision", "pending"),
                pipeline_name=self.extra_fields.get("pipeline_name", "editorial"),
                generation_hash=content_hash,
            )
        # strip keys that extra_fields will re-supply to avoid duplication
        for k in (
            "generator_class",
            "pipeline_name",
            "pipeline_hash",
            "component_count",
            "retrieved_doc_count",
            "user_facing_disclosure_shown",
            "node_class",
            "upstream_nodes",
            "public_interest_category",
            "human_editorial_review",
            "reviewer_id",
            "review_decision",
        ):
            self.extra_fields.pop(k, None)
        return base
