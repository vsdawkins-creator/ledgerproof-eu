"""ledgerproof-openai — Article 50 transparency receipts for the OpenAI Python SDK.

This package emits signed receipts on a side channel. It does **not** modify
the OpenAI response. It does **not** phone home. It does **not** claim
regulator endorsement or Article 40 presumption of conformity. See the
discipline section of the README.
"""

from .async_client_wrapper import LedgerProofAsyncOpenAI
from .canonical import canonical_encode, canonical_hash, canonical_hash_hex
from .client_wrapper import LedgerProofOpenAI
from .decorator import lpr_track
from .emitter import Emitter, LogEmitter, QueueEmitter, WebhookEmitter
from .manual import emit_receipt
from .schema import (
    SCHEMAS,
    AssistantResponseV1,
    ChatbotSessionV1,
    GeneratedContentV1,
    build_receipt,
)
from .signer import Ed25519Signer, HSMSigner, Signer
from .version import __version__

__all__ = [
    "__version__",
    # Clients
    "LedgerProofOpenAI",
    "LedgerProofAsyncOpenAI",
    # Patterns
    "lpr_track",
    "emit_receipt",
    # Schemas
    "ChatbotSessionV1",
    "GeneratedContentV1",
    "AssistantResponseV1",
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
