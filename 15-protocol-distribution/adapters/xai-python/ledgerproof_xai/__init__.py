"""ledgerproof-xai — Article 50 transparency receipts for xAI Grok.

xAI Grok uses an OpenAI-compatible REST API (`https://api.x.ai/v1`), so this
adapter wraps the official `openai` Python SDK configured for that base URL.

This package emits signed receipts on a side channel. It does **not** modify
the xAI response. It does **not** phone home. It does **not** claim regulator
endorsement, Article 40 presumption of conformity, or xAI endorsement. See the
discipline section of the README.
"""

from .async_client_wrapper import LedgerProofAsyncXAI
from .canonical import canonical_encode, canonical_hash, canonical_hash_hex
from .client_wrapper import XAI_DEFAULT_BASE_URL, LedgerProofXAI
from .decorator import lpr_track
from .emitter import Emitter, LogEmitter, QueueEmitter, WebhookEmitter
from .manual import emit_receipt
from .schema import (
    SCHEMAS,
    ChatbotSessionV1,
    GeneratedContentV1,
    RealtimeDataInferenceV1,
    VisionInferenceV1,
    build_receipt,
)
from .signer import Ed25519Signer, HSMSigner, Signer
from .version import __version__

__all__ = [
    "__version__",
    # Clients
    "LedgerProofXAI",
    "LedgerProofAsyncXAI",
    "XAI_DEFAULT_BASE_URL",
    # Patterns
    "lpr_track",
    "emit_receipt",
    # Schemas
    "ChatbotSessionV1",
    "GeneratedContentV1",
    "RealtimeDataInferenceV1",
    "VisionInferenceV1",
    "SCHEMAS",
    "build_receipt",
    # Signing
    "Signer",
    "Ed25519Signer",
    "HSMSigner",
    # Emitters
    "Emitter",
    "LogEmitter",
    "WebhookEmitter",
    "QueueEmitter",
    # Canonicalization
    "canonical_encode",
    "canonical_hash",
    "canonical_hash_hex",
]
