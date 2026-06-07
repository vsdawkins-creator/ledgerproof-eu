"""
LedgerProof adapter for the Google AI (Gemini) Python SDK.

Side-channel cryptographic transparency receipts for EU AI Act Article 50.

Discipline:
  - C1: No regulator/Google endorsement, no Article 40 presumption.
  - C4: Offline verification only; no phone-home.
  - C6: Stream-aware incremental SHA-256 over text deltas.
  - C7: Side-channel emission only; never modifies the Gemini response.

Not endorsed by Google. "Gemini" and "Google AI" are trademarks of Google LLC.
"""

from .chat_wrapper import LedgerProofChatSession
from .decorator import lpr_track
from .emitter import (
    Emitter,
    LogEmitter,
    MultiEmitter,
    QueueEmitter,
    StderrEmitter,
    WebhookEmitter,
)
from .manual import emit_receipt, extract_function_calls
from .model_wrapper import LedgerProofGenerativeModel
from .schema import (
    ContentRef,
    FunctionCallRef,
    Modality,
    ModelRef,
    ReceiptV1,
    RegulatoryContext,
    build_chatbot_session_receipt,
    build_function_call_receipt,
    build_generated_content_receipt,
    build_multimodal_generation_receipt,
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
    # wrappers
    "LedgerProofGenerativeModel",
    "LedgerProofChatSession",
    # decorator + manual
    "lpr_track",
    "emit_receipt",
    "extract_function_calls",
    # schemas
    "ContentRef",
    "FunctionCallRef",
    "Modality",
    "ModelRef",
    "ReceiptV1",
    "RegulatoryContext",
    "build_chatbot_session_receipt",
    "build_generated_content_receipt",
    "build_multimodal_generation_receipt",
    "build_function_call_receipt",
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
