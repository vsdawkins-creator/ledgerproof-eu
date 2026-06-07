"""ledgerproof-azure-openai — Article 50 transparency receipts for the Azure OpenAI Python SDK.

This package emits signed receipts on a side channel. It does **not** modify
the Azure OpenAI response. It does **not** phone home. It does **not** claim
regulator endorsement or Article 40 presumption of conformity. It is **not**
endorsed by Microsoft or Microsoft Azure.
"""

from .async_client_wrapper import LedgerProofAsyncAzureOpenAI
from .canonical import canonical_encode, canonical_hash, canonical_hash_hex
from .client_wrapper import LedgerProofAzureOpenAI
from .decorator import lpr_track
from .emitter import Emitter, LogEmitter, QueueEmitter, WebhookEmitter
from .manual import emit_receipt
from .schema import (
    SCHEMAS,
    AzureAdAuthenticatedSessionV1,
    AzureEnterpriseSessionV1,
    ChatbotSessionV1,
    GeneratedContentV1,
    build_receipt,
)
from .signer import AzureKeyVaultSigner, Ed25519Signer, HSMSigner, Signer
from .version import __version__

__all__ = [
    "__version__",
    # Clients
    "LedgerProofAzureOpenAI",
    "LedgerProofAsyncAzureOpenAI",
    # Patterns
    "lpr_track",
    "emit_receipt",
    # Schemas
    "ChatbotSessionV1",
    "GeneratedContentV1",
    "AzureEnterpriseSessionV1",
    "AzureAdAuthenticatedSessionV1",
    "SCHEMAS",
    "build_receipt",
    # Signing
    "Signer",
    "Ed25519Signer",
    "AzureKeyVaultSigner",
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
