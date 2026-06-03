"""
LedgerProof adapter for the Voyage AI Python SDK (embeddings + rerank).

Side-channel cryptographic transparency receipts for EU AI Act Article 50 RAG
pipeline evidence. Voyage AI is upstream RAG infrastructure; this adapter binds
embedding + rerank evidence to a downstream chatbot turn so the full
retrieval -> generation chain is cryptographically verifiable.

Discipline:
  - C1: No regulator endorsement. No Article 40 presumption of conformity.
        Not endorsed by Voyage AI / MongoDB.
  - C4: Offline verification only; no phone-home.
  - C6: Stream-aware SHA-256 primitives available for downstream chat receipts.
  - C7: Side-channel emission only; never modifies the Voyage response.
"""

from .async_client_wrapper import LedgerProofAsyncVoyage
from .client_wrapper import LedgerProofVoyage
from .decorator import lpr_track_embed, lpr_track_rerank
from .emitter import (
    Emitter,
    LogEmitter,
    MultiEmitter,
    QueueEmitter,
    StderrEmitter,
    WebhookEmitter,
)
from .manual import (
    build_embedding_refs,
    build_rerank_result_refs,
    build_voyage_model_ref,
    emit_embedding_receipt,
    emit_rag_pipeline_receipt,
    emit_rerank_receipt,
    extract_embeddings,
    extract_rerank_results,
    extract_total_tokens,
)
from .schema import (
    DownstreamChatRef,
    EmbeddingRef,
    ReceiptV1,
    RegulatoryContext,
    RerankResultRef,
    UpstreamReceiptRef,
    VoyageModelRef,
    build_embedding_inference_receipt,
    build_rag_pipeline_evidence_receipt,
    build_rerank_inference_receipt,
)
from .signer import (
    AwsKmsEd25519Signer,
    Ed25519Signer,
    GcpKmsEd25519Signer,
    Signer,
    verify,
)
from .version import __version__

__all__ = [
    "__version__",
    # client wrappers
    "LedgerProofVoyage",
    "LedgerProofAsyncVoyage",
    # decorators
    "lpr_track_embed",
    "lpr_track_rerank",
    # manual
    "emit_embedding_receipt",
    "emit_rerank_receipt",
    "emit_rag_pipeline_receipt",
    "build_embedding_refs",
    "build_rerank_result_refs",
    "build_voyage_model_ref",
    "extract_embeddings",
    "extract_rerank_results",
    "extract_total_tokens",
    # schemas
    "EmbeddingRef",
    "RerankResultRef",
    "UpstreamReceiptRef",
    "DownstreamChatRef",
    "VoyageModelRef",
    "ReceiptV1",
    "RegulatoryContext",
    "build_embedding_inference_receipt",
    "build_rerank_inference_receipt",
    "build_rag_pipeline_evidence_receipt",
    # emitters
    "Emitter",
    "LogEmitter",
    "StderrEmitter",
    "WebhookEmitter",
    "QueueEmitter",
    "MultiEmitter",
    # signers
    "Signer",
    "Ed25519Signer",
    "AwsKmsEd25519Signer",
    "GcpKmsEd25519Signer",
    "verify",
]
