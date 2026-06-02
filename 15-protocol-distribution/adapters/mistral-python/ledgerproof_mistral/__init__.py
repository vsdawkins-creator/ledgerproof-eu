"""
LedgerProof adapter for the Mistral Python SDK (`mistralai>=1.0`).

Side-channel cryptographic transparency receipts for EU AI Act Article 50 evidence.

Strategic note: Mistral is a French / EU-headquartered model provider. This
adapter ships an EU-sovereign-AI attribution schema (`eu_sovereign_ai_session/v1`)
so deployers can record EU residency / control facts alongside their Article 50
transparency evidence.

Discipline:
  - C1: No regulator endorsement, no Article 40 presumption of conformity.
  - C4: Offline verification only; no phone-home.
  - C6: Stream-aware SHA-256 over text deltas.
  - C7: Side-channel emission only; never modifies the Mistral response.
"""

from .async_client_wrapper import LedgerProofAsyncMistral
from .client_wrapper import LedgerProofMistral
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
    EuSovereigntyAttestation,
    ModelRef,
    ReceiptV1,
    RegulatoryContext,
    ToolUseRef,
    build_chatbot_session_receipt,
    build_eu_sovereign_ai_session_receipt,
    build_generated_content_receipt,
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
    "LedgerProofMistral",
    "LedgerProofAsyncMistral",
    # decorator
    "lpr_track",
    # manual
    "emit_receipt",
    "extract_tool_uses",
    # schemas
    "ContentRef",
    "EuSovereigntyAttestation",
    "ModelRef",
    "ReceiptV1",
    "RegulatoryContext",
    "ToolUseRef",
    "build_chatbot_session_receipt",
    "build_generated_content_receipt",
    "build_eu_sovereign_ai_session_receipt",
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
