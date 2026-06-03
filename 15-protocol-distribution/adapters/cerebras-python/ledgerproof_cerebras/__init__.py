"""LedgerProof adapter for the Cerebras Cloud Python SDK.

Open cryptographic protocol for EU AI Act Article 50 transparency receipts.
Foundation-stewarded. Not endorsed by Cerebras Systems, Inc.
Not endorsed by the European Commission or any EU supervisory authority.
Does not, on its own, satisfy Article 50.
Does not confer an Article 40 presumption of conformity.
"""

from .version import __version__, PROTOCOL_VERSION, ADAPTER_NAME
from .client_wrapper import LedgerProofCerebras
from .async_client_wrapper import LedgerProofAsyncCerebras
from .decorator import lpr_track
from .manual import emit_receipt
from .schema import (
    ReceiptSchemaName,
    ChatbotSessionV1,
    GeneratedContentV1,
    WaferScaleInferenceV1,
    ReasoningDistilledV1,
    validate_gdpr_safe,
    GDPRValidationError,
    hash_str,
)
from .signer import Ed25519Signer, load_signer_from_pem

__all__ = [
    "__version__",
    "PROTOCOL_VERSION",
    "ADAPTER_NAME",
    "LedgerProofCerebras",
    "LedgerProofAsyncCerebras",
    "lpr_track",
    "emit_receipt",
    "ReceiptSchemaName",
    "ChatbotSessionV1",
    "GeneratedContentV1",
    "WaferScaleInferenceV1",
    "ReasoningDistilledV1",
    "validate_gdpr_safe",
    "GDPRValidationError",
    "hash_str",
    "Ed25519Signer",
    "load_signer_from_pem",
]
