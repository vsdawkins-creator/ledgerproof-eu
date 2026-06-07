"""
Manual receipt emission for Voyage AI EmbeddingsObject / RerankingObject.

Use for full control over when and how a receipt fires, or for non-standard
call shapes (batch jobs, multimodal embeddings, contextualized embeddings).
"""

from __future__ import annotations

import base64
import hashlib
import uuid
from typing import Any, Iterable

from .canonical import (
    canonical_encode,
    canonicalize_vector,
    hash_text,
)
from .emitter import Emitter, LogEmitter
from .schema import (
    DownstreamChatRef,
    EmbeddingRef,
    RegulatoryContext,
    RerankResultRef,
    ReceiptV1,
    UpstreamReceiptRef,
    VoyageModelRef,
    build_embedding_inference_receipt,
    build_rag_pipeline_evidence_receipt,
    build_rerank_inference_receipt,
)
from .signer import Ed25519Signer, Signer
from .version import __version__


def _default_regulatory_context_supporting() -> RegulatoryContext:
    """Embed/rerank receipts default to article_50_paragraph='supporting'."""
    return RegulatoryContext(
        article_50_paragraph="supporting",
        deployer_jurisdiction="EU",
        end_user_disclosure_made=True,
    )


def _default_regulatory_context_chat() -> RegulatoryContext:
    return RegulatoryContext(
        article_50_paragraph="1",
        deployer_jurisdiction="EU",
        end_user_disclosure_made=True,
    )


def _resolve_reg_ctx(
    regulatory_context: RegulatoryContext | dict[str, Any] | None,
    *,
    default_chat: bool = False,
) -> RegulatoryContext:
    if regulatory_context is None:
        return (
            _default_regulatory_context_chat()
            if default_chat
            else _default_regulatory_context_supporting()
        )
    if isinstance(regulatory_context, dict):
        return RegulatoryContext(**regulatory_context)
    return regulatory_context


# ---------------------------------------------------------------------------
# Helpers — extract from Voyage EmbeddingsObject / RerankingObject
# ---------------------------------------------------------------------------


def extract_embeddings(result: Any) -> list[list[float]]:
    """
    Pull `.embeddings` off a Voyage EmbeddingsObject.

    Voyage shape (voyageai>=0.3):
        result.embeddings : List[List[float]]
        result.total_tokens : int

    We tolerate dict-shaped fixtures and attribute access.
    """
    if result is None:
        return []
    embeds = getattr(result, "embeddings", None)
    if embeds is None and isinstance(result, dict):
        embeds = result.get("embeddings")
    if embeds is None:
        return []
    return [list(v) for v in embeds]


def extract_total_tokens(result: Any) -> int | None:
    if result is None:
        return None
    tokens = getattr(result, "total_tokens", None)
    if tokens is None and isinstance(result, dict):
        tokens = result.get("total_tokens")
    return int(tokens) if tokens is not None else None


def extract_rerank_results(result: Any) -> list[Any]:
    """
    Voyage rerank shape:
        result.results : list of objects with
            .index (int)
            .document (str)
            .relevance_score (float)
        result.total_tokens : int
    """
    if result is None:
        return []
    results = getattr(result, "results", None)
    if results is None and isinstance(result, dict):
        results = result.get("results")
    return list(results or [])


# ---------------------------------------------------------------------------
# Build helpers
# ---------------------------------------------------------------------------


def build_embedding_refs(
    inputs: list[str],
    vectors: list[list[float]],
) -> list[EmbeddingRef]:
    """Build EmbeddingRef list from raw inputs + returned vectors."""
    if len(inputs) != len(vectors):
        raise ValueError(
            f"inputs/vectors length mismatch: {len(inputs)} inputs vs {len(vectors)} vectors"
        )
    refs: list[EmbeddingRef] = []
    for i, (text, vec) in enumerate(zip(inputs, vectors)):
        encoded = text.encode("utf-8") if isinstance(text, str) else bytes(text)
        vec_bytes = canonicalize_vector(vec)
        refs.append(
            EmbeddingRef(
                input_sha256_hex=hashlib.sha256(encoded).hexdigest(),
                input_byte_length=len(encoded),
                vector_sha256_hex=hashlib.sha256(vec_bytes).hexdigest(),
                vector_dim=len(vec),
                input_index=i,
            )
        )
    return refs


def build_rerank_result_refs(
    documents: list[str],
    voyage_results: Iterable[Any],
    document_ids: list[str] | None = None,
) -> list[RerankResultRef]:
    """
    Build RerankResultRef list from the original candidate `documents` list and
    Voyage's reranking results.

    Each Voyage result exposes `.index` (into `documents`), `.document` (the
    text), and `.relevance_score`. We hash the document text from `documents`
    (the source of truth the caller supplied) so the receipt binds what the
    caller actually fed in.
    """
    doc_bytes: list[bytes] = []
    for d in documents:
        if isinstance(d, str):
            doc_bytes.append(d.encode("utf-8"))
        else:
            doc_bytes.append(bytes(d))

    refs: list[RerankResultRef] = []
    for rank_pos, r in enumerate(voyage_results):
        idx = getattr(r, "index", None)
        if idx is None and isinstance(r, dict):
            idx = r.get("index")
        if idx is None:
            continue
        idx = int(idx)
        score = getattr(r, "relevance_score", None)
        if score is None and isinstance(r, dict):
            score = r.get("relevance_score")
        if score is None:
            continue
        # Clamp into [0, 1] for schema validity. Voyage rerank-2 scores are
        # normalized in this range; we clamp defensively.
        score_f = max(0.0, min(1.0, float(score)))

        if 0 <= idx < len(doc_bytes):
            d_bytes = doc_bytes[idx]
        else:
            d_bytes = b""
        doc_id = None
        if document_ids and 0 <= idx < len(document_ids):
            doc_id = str(document_ids[idx])[:256]

        refs.append(
            RerankResultRef(
                document_id=doc_id,
                document_sha256_hex=hashlib.sha256(d_bytes).hexdigest(),
                document_byte_length=len(d_bytes),
                original_index=idx,
                rerank_position=rank_pos,
                relevance_score=score_f,
            )
        )
    return refs


def build_voyage_model_ref(
    *,
    model: str,
    input_type: str | None = None,
    output_dtype: str | None = None,
    total_tokens: int | None = None,
    response_id: str | None = None,
) -> VoyageModelRef:
    """Build a VoyageModelRef. Voyage assigns no response ID, so we synthesize one."""
    it_norm: str | None = None
    if input_type is not None:
        if input_type in ("document", "query"):
            it_norm = input_type
        else:
            it_norm = "none"
    return VoyageModelRef(
        model_id=model,
        response_id=response_id or f"voyage-{uuid.uuid4().hex[:16]}",
        input_type=it_norm,
        output_dtype=output_dtype,
        total_tokens=total_tokens,
    )


# ---------------------------------------------------------------------------
# emit_receipt — top-level convenience for the three schemas
# ---------------------------------------------------------------------------


def emit_embedding_receipt(
    *,
    deployer_id: str,
    model: str,
    inputs: list[str],
    result: Any,
    input_type: str | None = None,
    output_dtype: str | None = None,
    regulatory_context: RegulatoryContext | dict[str, Any] | None = None,
    signer: Signer | None = None,
    emitter: Emitter | None = None,
) -> dict[str, Any]:
    """Build, sign, and emit an embedding_inference/v1 receipt."""
    signer = signer or Ed25519Signer()
    emitter = emitter or LogEmitter()
    reg_ctx = _resolve_reg_ctx(regulatory_context)

    vectors = extract_embeddings(result)
    total_tokens = extract_total_tokens(result)
    embedding_refs = build_embedding_refs(inputs, vectors)

    model_ref = build_voyage_model_ref(
        model=model,
        input_type=input_type,
        output_dtype=output_dtype,
        total_tokens=total_tokens,
    )

    receipt = build_embedding_inference_receipt(
        receipt_id=str(uuid.uuid4()),
        deployer_id=deployer_id,
        model=model_ref,
        regulatory_context=reg_ctx,
        embeddings=embedding_refs,
        adapter_version=__version__,
    )
    return _sign_and_emit(receipt, signer, emitter)


def emit_rerank_receipt(
    *,
    deployer_id: str,
    model: str,
    query: str,
    documents: list[str],
    result: Any,
    document_ids: list[str] | None = None,
    regulatory_context: RegulatoryContext | dict[str, Any] | None = None,
    signer: Signer | None = None,
    emitter: Emitter | None = None,
) -> dict[str, Any]:
    """Build, sign, and emit a rerank_inference/v1 receipt."""
    signer = signer or Ed25519Signer()
    emitter = emitter or LogEmitter()
    reg_ctx = _resolve_reg_ctx(regulatory_context)

    voyage_results = extract_rerank_results(result)
    total_tokens = extract_total_tokens(result)
    rerank_refs = build_rerank_result_refs(documents, voyage_results, document_ids=document_ids)

    query_bytes = query.encode("utf-8")
    model_ref = build_voyage_model_ref(model=model, total_tokens=total_tokens)

    receipt = build_rerank_inference_receipt(
        receipt_id=str(uuid.uuid4()),
        deployer_id=deployer_id,
        model=model_ref,
        regulatory_context=reg_ctx,
        rerank_query_sha256_hex=hashlib.sha256(query_bytes).hexdigest(),
        rerank_query_byte_length=len(query_bytes),
        rerank_results=rerank_refs,
        adapter_version=__version__,
    )
    return _sign_and_emit(receipt, signer, emitter)


def emit_rag_pipeline_receipt(
    *,
    deployer_id: str,
    upstream_signed_receipts: list[dict[str, Any]],
    downstream_signed_receipt: dict[str, Any],
    downstream_adapter: str,
    user_query: str,
    assistant_response: str | None = None,
    rag_pipeline_model_id: str = "voyage-rag-pipeline",
    regulatory_context: RegulatoryContext | dict[str, Any] | None = None,
    signer: Signer | None = None,
    emitter: Emitter | None = None,
) -> dict[str, Any]:
    """
    Build, sign, and emit a rag_pipeline_evidence/v1 receipt.

    Inputs are signed-receipt dicts (the output of the upstream emit_*_receipt
    calls and a downstream LedgerProof chat-adapter receipt). We compute the
    canonical CBOR SHA-256 of each upstream/downstream `receipt` payload and
    bind it cryptographically.
    """
    signer = signer or Ed25519Signer()
    emitter = emitter or LogEmitter()
    reg_ctx = _resolve_reg_ctx(regulatory_context, default_chat=True)

    upstream_refs: list[UpstreamReceiptRef] = []
    for sr in upstream_signed_receipts:
        payload = sr.get("receipt") if isinstance(sr, dict) else None
        if payload is None:
            raise ValueError("upstream_signed_receipts entries must be {receipt: ...} dicts")
        schema_name = payload.get("schema")
        if schema_name not in ("embedding_inference/v1", "rerank_inference/v1"):
            raise ValueError(
                f"upstream receipt schema {schema_name!r} not allowed in "
                "rag_pipeline_evidence/v1; must be embedding_inference/v1 or rerank_inference/v1"
            )
        receipt_id = payload.get("receipt_id") or "unknown"
        canonical_hex = hashlib.sha256(canonical_encode(payload)).hexdigest()
        upstream_refs.append(
            UpstreamReceiptRef(
                schema_name=schema_name,
                receipt_id=str(receipt_id),
                receipt_canonical_sha256_hex=canonical_hex,
            )
        )

    down_payload = downstream_signed_receipt.get("receipt") if isinstance(downstream_signed_receipt, dict) else None
    if down_payload is None:
        raise ValueError("downstream_signed_receipt must be a {receipt: ...} dict")
    down_canonical = hashlib.sha256(canonical_encode(down_payload)).hexdigest()
    down_receipt_id = str(down_payload.get("receipt_id") or "unknown")

    user_query_hash = hash_text(user_query).hex()
    assistant_hash = hash_text(assistant_response).hex() if assistant_response is not None else None

    downstream_ref = DownstreamChatRef(
        downstream_adapter=downstream_adapter,
        downstream_receipt_id=down_receipt_id,
        downstream_receipt_canonical_sha256_hex=down_canonical,
        user_query_sha256_hex=user_query_hash,
        assistant_response_sha256_hex=assistant_hash,
    )

    model_ref = build_voyage_model_ref(
        model=rag_pipeline_model_id,
        response_id=f"rag-{uuid.uuid4().hex[:16]}",
    )

    receipt = build_rag_pipeline_evidence_receipt(
        receipt_id=str(uuid.uuid4()),
        deployer_id=deployer_id,
        model=model_ref,
        regulatory_context=reg_ctx,
        upstream_receipts=upstream_refs,
        downstream_chat=downstream_ref,
        adapter_version=__version__,
    )
    return _sign_and_emit(receipt, signer, emitter)


def _sign_and_emit(
    receipt: ReceiptV1,
    signer: Signer,
    emitter: Emitter,
) -> dict[str, Any]:
    payload = receipt.to_payload()
    canonical_bytes = canonical_encode(payload)
    signature = signer.sign(canonical_bytes)
    signed = {
        "receipt": payload,
        "signature_alg": "ed25519",
        "signature_b64": base64.b64encode(signature).decode("ascii"),
        "signer_key_id": signer.key_id,
        "canonical_encoding": "cbor-rfc8949-deterministic",
    }
    emitter.emit(signed)
    return signed
