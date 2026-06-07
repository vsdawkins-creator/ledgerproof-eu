"""
LedgerProof adapter for Mistral Codestral (`mistralai>=1.0`, Codestral endpoint).

Side-channel cryptographic transparency receipts for EU AI Act Article 50 evidence,
specialised for the AI-generated-code case: license compliance, security review,
attribution, editorial oversight for safety-critical code.

C1 reminder: not endorsed by Mistral AI SAS, the European Commission, the AI Office,
or any national competent authority. Not a presumption of conformity under Article 40.

Discipline:
  - C1: No regulator / vendor endorsement, no Article 40.
  - C4: Offline verification only; no phone-home.
  - C6: Stream-aware SHA-256 over text deltas.
  - C7: Side-channel emission only; never modifies the Codestral response.
"""

from .async_wrapper import LedgerProofAsyncCodestral
from .codestral_wrapper import DEFAULT_CODESTRAL_URL, LedgerProofCodestral
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
    emit_receipt,
    emit_safety_critical_review_receipt,
    extract_tool_uses,
)
from .schema import (
    ContentRef,
    FimPositions,
    GeneratedCodeAttributes,
    ModelRef,
    ReceiptV1,
    RegulatoryContext,
    SafetyCriticalReview,
    ToolUseRef,
    build_chatbot_session_receipt,
    build_fim_completion_receipt,
    build_generated_code_receipt,
    build_safety_critical_code_review_receipt,
)
from .signer import (
    AwsKmsEd25519Signer,
    AzureKeyVaultEd25519Signer,
    Ed25519Signer,
    GcpKmsEd25519Signer,
    Signer,
    verify,
)
from .version import __version__

__all__ = [
    "__version__",
    # client wrappers
    "LedgerProofCodestral",
    "LedgerProofAsyncCodestral",
    "DEFAULT_CODESTRAL_URL",
    # decorator
    "lpr_track",
    # manual
    "emit_receipt",
    "emit_safety_critical_review_receipt",
    "extract_tool_uses",
    # schemas
    "ContentRef",
    "FimPositions",
    "GeneratedCodeAttributes",
    "ModelRef",
    "ReceiptV1",
    "RegulatoryContext",
    "SafetyCriticalReview",
    "ToolUseRef",
    "build_chatbot_session_receipt",
    "build_generated_code_receipt",
    "build_fim_completion_receipt",
    "build_safety_critical_code_review_receipt",
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
    "AzureKeyVaultEd25519Signer",
    "verify",
]
