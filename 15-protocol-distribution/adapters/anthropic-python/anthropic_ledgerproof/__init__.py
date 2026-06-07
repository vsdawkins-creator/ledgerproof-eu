"""
LedgerProof adapter for the Anthropic Python SDK.

Side-channel cryptographic transparency receipts for EU AI Act Article 50 evidence.

Discipline:
  - C1: No regulator endorsement, no Article 40 presumption of conformity.
  - C4: Offline verification only; no phone-home.
  - C6: Stream-aware SHA-256 over text deltas.
  - C7: Side-channel emission only; never modifies the Anthropic response.
"""

from .async_client_wrapper import LedgerProofAsyncAnthropic
from .client_wrapper import LedgerProofAnthropic
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
    ModelRef,
    ReceiptV1,
    RegulatoryContext,
    ToolUseRef,
    build_agent_action_receipt,
    build_chatbot_session_receipt,
    build_generated_content_receipt,
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
    "LedgerProofAnthropic",
    "LedgerProofAsyncAnthropic",
    # decorator
    "lpr_track",
    # manual
    "emit_receipt",
    "extract_tool_uses",
    # schemas
    "ContentRef",
    "ModelRef",
    "ReceiptV1",
    "RegulatoryContext",
    "ToolUseRef",
    "build_chatbot_session_receipt",
    "build_generated_content_receipt",
    "build_agent_action_receipt",
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
