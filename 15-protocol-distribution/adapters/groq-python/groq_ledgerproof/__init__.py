"""LedgerProof adapter for the Groq Python SDK.

Open cryptographic protocol for EU AI Act Article 50 transparency receipts.
Foundation-stewarded. Not endorsed by Groq, Inc.
Not endorsed by the European Commission or any EU supervisory authority.
Does not, on its own, satisfy Article 50.
Does not confer an Article 40 presumption of conformity.
"""

from .version import __version__, PROTOCOL_VERSION, ADAPTER_NAME
from .client_wrapper import LedgerProofGroq
from .async_client_wrapper import LedgerProofAsyncGroq
from .decorator import lpr_track
from .manual import emit_receipt
from .schema import (
    ReceiptSchemaName,
    ChatbotSessionV1,
    GeneratedContentV1,
    LowLatencyInferenceV1,
    AudioTranscriptionV1,
    validate_gdpr_safe,
    GDPRValidationError,
    hash_str,
)
from .signer import Ed25519Signer, load_signer_from_pem

__all__ = [
    "__version__",
    "PROTOCOL_VERSION",
    "ADAPTER_NAME",
    "LedgerProofGroq",
    "LedgerProofAsyncGroq",
    "lpr_track",
    "emit_receipt",
    "ReceiptSchemaName",
    "ChatbotSessionV1",
    "GeneratedContentV1",
    "LowLatencyInferenceV1",
    "AudioTranscriptionV1",
    "validate_gdpr_safe",
    "GDPRValidationError",
    "hash_str",
    "Ed25519Signer",
    "load_signer_from_pem",
]
