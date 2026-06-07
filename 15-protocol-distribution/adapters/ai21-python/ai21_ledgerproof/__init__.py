"""
LedgerProof adapter for the AI21 Labs Python SDK (`ai21>=3.0`).

Side-channel cryptographic transparency receipts for EU AI Act Article 50 evidence.

Strategic note: AI21 Labs ships the Jamba family — a Mamba/Transformer hybrid
architecture with up to 256k context. This adapter ships dedicated
`long_context_inference/v1` and `jamba_hybrid_attribution/v1` schemas so deployers
exercising those differentiators can record them inline with Article 50 receipts.

Discipline:
  - C1: No regulator endorsement, no Article 40 presumption of conformity.
        No AI21 Labs endorsement.
  - C4: Offline verification only; no phone-home.
  - C6: Stream-aware SHA-256 over text deltas (critical for 256k-token streams).
  - C7: Side-channel emission only; never modifies the AI21 response.
"""

from .async_client_wrapper import LedgerProofAsyncAI21
from .client_wrapper import LedgerProofAI21
from .decorator import lpr_track
from .emitter import (
    Emitter,
    LogEmitter,
    MultiEmitter,
    QueueEmitter,
    StderrEmitter,
    WebhookEmitter,
)
from .manual import emit_receipt, extract_tool_uses
from .schema import (
    ContentRef,
    JambaHybridAttestation,
    LongContextAttestation,
    ModelRef,
    ReceiptV1,
    RegulatoryContext,
    ToolUseRef,
    build_chatbot_session_receipt,
    build_generated_content_receipt,
    build_jamba_hybrid_attribution_receipt,
    build_long_context_inference_receipt,
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
    "LedgerProofAI21",
    "LedgerProofAsyncAI21",
    # decorator
    "lpr_track",
    # manual
    "emit_receipt",
    "extract_tool_uses",
    # schemas
    "ContentRef",
    "JambaHybridAttestation",
    "LongContextAttestation",
    "ModelRef",
    "ReceiptV1",
    "RegulatoryContext",
    "ToolUseRef",
    "build_chatbot_session_receipt",
    "build_generated_content_receipt",
    "build_long_context_inference_receipt",
    "build_jamba_hybrid_attribution_receipt",
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
