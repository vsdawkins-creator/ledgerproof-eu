"""ledgerproof-deepseek — Article 50 transparency receipts for DeepSeek.

DeepSeek uses an OpenAI-compatible REST API (`https://api.deepseek.com`), so
this adapter wraps the official `openai` Python SDK configured for that base
URL.

This package emits signed receipts on a side channel. It does **not** modify
the DeepSeek response. It does **not** phone home. It does **not** claim
regulator endorsement, Article 40 presumption of conformity, or DeepSeek
endorsement. See the discipline section of the README.
"""

from .async_client_wrapper import LedgerProofAsyncDeepSeek
from .canonical import canonical_encode, canonical_hash, canonical_hash_hex
from .client_wrapper import DEEPSEEK_DEFAULT_BASE_URL, LedgerProofDeepSeek
from .decorator import lpr_track
from .emitter import (
    Emitter,
    LogEmitter,
    MultiEmitter,
    QueueEmitter,
    StderrEmitter,
    WebhookEmitter,
)
from .manual import emit_receipt
from .schema import (
    SCHEMAS,
    ChatbotSessionV1,
    CodeGenerationV1,
    GeneratedContentV1,
    ReasoningTraceV1,
    build_receipt,
)
from .signer import Ed25519Signer, HSMSigner, Signer
from .version import __version__

__all__ = [
    "__version__",
    # Clients
    "LedgerProofDeepSeek",
    "LedgerProofAsyncDeepSeek",
    "DEEPSEEK_DEFAULT_BASE_URL",
    # Patterns
    "lpr_track",
    "emit_receipt",
    # Schemas
    "ChatbotSessionV1",
    "GeneratedContentV1",
    "ReasoningTraceV1",
    "CodeGenerationV1",
    "SCHEMAS",
    "build_receipt",
    # Signing
    "Signer",
    "Ed25519Signer",
    "HSMSigner",
    # Emitters
    "Emitter",
    "LogEmitter",
    "StderrEmitter",
    "WebhookEmitter",
    "QueueEmitter",
    "MultiEmitter",
    # Canonicalization
    "canonical_encode",
    "canonical_hash",
    "canonical_hash_hex",
]
