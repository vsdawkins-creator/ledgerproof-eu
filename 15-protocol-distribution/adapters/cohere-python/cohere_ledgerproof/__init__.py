"""
LedgerProof adapter for the Cohere Python SDK.

Side-channel cryptographic transparency receipts for EU AI Act Article 50 evidence.

Discipline:
  - C1: No regulator endorsement, no Article 40 presumption of conformity.
  - C4: Offline verification only; no phone-home.
  - C6: Stream-aware SHA-256 over text deltas.
  - C7: Side-channel emission only; never modifies the Cohere response.
"""

from .async_client_wrapper import LedgerProofAsyncCohere
from .client_wrapper import LedgerProofCohere
from .decorator import lpr_track
from .emitter import (
    Emitter,
    LogEmitter,
    MultiEmitter,
    QueueEmitter,
    StderrEmitter,
    WebhookEmitter,
)
from .manual import (
    build_disclosure_ref,
    build_retrieved_document_refs,
    emit_receipt,
    extract_assistant_text,
    extract_tool_uses,
)
from .schema import (
    ContentRef,
    DisclosureRef,
    ModelRef,
    ReceiptV1,
    RegulatoryContext,
    RetrievedDocumentRef,
    ToolUseRef,
    build_chatbot_session_receipt,
    build_generated_content_receipt,
    build_multilingual_disclosure_receipt,
    build_rag_response_receipt,
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
    "LedgerProofCohere",
    "LedgerProofAsyncCohere",
    # decorator
    "lpr_track",
    # manual
    "emit_receipt",
    "extract_assistant_text",
    "extract_tool_uses",
    "build_retrieved_document_refs",
    "build_disclosure_ref",
    # schemas
    "ContentRef",
    "DisclosureRef",
    "ModelRef",
    "ReceiptV1",
    "RegulatoryContext",
    "RetrievedDocumentRef",
    "ToolUseRef",
    "build_chatbot_session_receipt",
    "build_generated_content_receipt",
    "build_rag_response_receipt",
    "build_multilingual_disclosure_receipt",
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
