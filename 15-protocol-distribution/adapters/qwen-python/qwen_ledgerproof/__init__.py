"""
LedgerProof adapter for the Alibaba DashScope / Qwen Python SDK (`dashscope>=1.20`).

Side-channel cryptographic transparency receipts for EU AI Act Article 50 evidence.

Strategic note: Qwen is a Chinese-origin foundation model family operated by
Alibaba Cloud. This adapter ships two Qwen-specific schemas
(`multilingual_chinese_inference/v1` and `cross_jurisdictional_routing/v1`) so
deployers can record Chinese-language disclosure facts and the choice of
non-mainland regional endpoint (Singapore / Hong Kong) alongside their
Article 50 transparency evidence. The attestation blocks are descriptive
deployer-asserted metadata only — see C1 disclaimer in README.

Discipline:
  - C1: No regulator endorsement, no Article 40 presumption of conformity,
    no endorsement from Alibaba Cloud or any Chinese regulator.
  - C4: Offline verification only; no phone-home.
  - C6: Stream-aware SHA-256 over text deltas (handles DashScope's cumulative
    streaming default).
  - C7: Side-channel emission only; never modifies the DashScope response.
"""

from .async_client_wrapper import LedgerProofAsyncQwen
from .client_wrapper import LedgerProofQwen
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
    ChineseInferenceAttestation,
    ContentRef,
    CrossJurisdictionalRoute,
    ModelRef,
    ReceiptV1,
    RegulatoryContext,
    ToolUseRef,
    build_chatbot_session_receipt,
    build_cross_jurisdictional_routing_receipt,
    build_generated_content_receipt,
    build_multilingual_chinese_inference_receipt,
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
    "LedgerProofQwen",
    "LedgerProofAsyncQwen",
    # decorator
    "lpr_track",
    # manual
    "emit_receipt",
    "extract_tool_uses",
    # schemas
    "ChineseInferenceAttestation",
    "ContentRef",
    "CrossJurisdictionalRoute",
    "ModelRef",
    "ReceiptV1",
    "RegulatoryContext",
    "ToolUseRef",
    "build_chatbot_session_receipt",
    "build_generated_content_receipt",
    "build_multilingual_chinese_inference_receipt",
    "build_cross_jurisdictional_routing_receipt",
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
