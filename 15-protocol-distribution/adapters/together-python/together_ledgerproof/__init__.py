"""
LedgerProof adapter for the Together.ai Python SDK (`together>=1.3`).

Side-channel cryptographic transparency receipts for EU AI Act Article 50
evidence.

Strategic note: Together hosts open-weights models built by other organisations
(Meta Llama, Mistral, Qwen/Alibaba, DeepSeek, Black Forest Labs / FLUX, ...).
This adapter ships an `open_model_inference/v1` schema so deployers can record
both the underlying model provider AND the Together hosting attribution.

Discipline:
  - C1: No regulator endorsement, no Article 40 presumption of conformity.
       Not endorsed by, affiliated with, or certified by Together AI Inc.
  - C4: Offline verification only; no phone-home.
  - C6: Stream-aware SHA-256 over text deltas.
  - C7: Side-channel emission only; never modifies the Together response.
"""

from .async_client_wrapper import LedgerProofAsyncTogether
from .client_wrapper import LedgerProofTogether
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
    emit_image_generation_receipt,
    emit_receipt,
    extract_tool_uses,
)
from .schema import (
    ContentRef,
    ModelRef,
    OpenModelAttribution,
    ReceiptV1,
    RegulatoryContext,
    ToolUseRef,
    build_chatbot_session_receipt,
    build_generated_content_receipt,
    build_image_generation_receipt,
    build_open_model_inference_receipt,
    infer_open_model_attribution,
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
    "LedgerProofTogether",
    "LedgerProofAsyncTogether",
    # decorator
    "lpr_track",
    # manual
    "emit_receipt",
    "emit_image_generation_receipt",
    "extract_tool_uses",
    # schemas
    "ContentRef",
    "ModelRef",
    "OpenModelAttribution",
    "ReceiptV1",
    "RegulatoryContext",
    "ToolUseRef",
    "build_chatbot_session_receipt",
    "build_generated_content_receipt",
    "build_open_model_inference_receipt",
    "build_image_generation_receipt",
    "infer_open_model_attribution",
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
