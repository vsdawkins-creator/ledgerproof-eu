"""
LedgerProof adapter for the Reka AI Python SDK.

Side-channel cryptographic transparency receipts for EU AI Act Article 50
evidence, with first-class support for Reka's multimodal-native inference
surface (text + image + audio + video in a single inference).

Discipline:
  - C1: No regulator endorsement, no Article 40 presumption of conformity.
        Not endorsed by Reka AI.
  - C4: Offline verification only; no phone-home. URLs in media blocks are
        hashed by URI, never dereferenced.
  - C6: Stream-aware SHA-256 over text deltas.
  - C7: Side-channel emission only; never modifies the Reka response.
"""

from .async_client_wrapper import LedgerProofAsyncReka
from .client_wrapper import LedgerProofReka
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
    MediaRef,
    Modality,
    ModelRef,
    ReceiptV1,
    RegulatoryContext,
    ToolUseRef,
    build_chatbot_session_receipt,
    build_generated_content_receipt,
    build_multimodal_native_inference_receipt,
    build_video_understanding_receipt,
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
    "LedgerProofReka",
    "LedgerProofAsyncReka",
    # decorator
    "lpr_track",
    # manual
    "emit_receipt",
    "extract_tool_uses",
    # schemas
    "ContentRef",
    "MediaRef",
    "Modality",
    "ModelRef",
    "ReceiptV1",
    "RegulatoryContext",
    "ToolUseRef",
    "build_chatbot_session_receipt",
    "build_generated_content_receipt",
    "build_multimodal_native_inference_receipt",
    "build_video_understanding_receipt",
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
