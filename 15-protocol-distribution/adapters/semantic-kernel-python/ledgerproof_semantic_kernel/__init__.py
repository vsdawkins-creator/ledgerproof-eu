"""ledgerproof-semantic-kernel

Semantic Kernel (Python) adapter for the LedgerProof protocol. Emits signed
EU AI Act Article 50 transparency receipts as a side channel.

Verification is offline (C4). Receipts go to log / queue / webhook (C7).
The chat-service wrapper is stream-aware (C6). The LLM / function response
payload is never modified by this adapter.
"""

from .chat_service_wrapper import LedgerProofChatService
from .decorator import lpr_track
from .emitter import BaseEmitter, LogEmitter, QueueEmitter, WebhookEmitter
from .manual import emit_receipt
from .schema import (
    SCHEMAS,
    AgentFunctionInvocationReceipt,
    AzureEnterpriseSessionReceipt,
    ChatbotSessionReceipt,
    GeneratedContentReceipt,
    get_schema,
)
from .signer import BaseSigner, Ed25519Signer
from .version import __version__

# Filters are optional — they require semantic-kernel to be installed.
try:
    from .filters import (  # noqa: F401
        LedgerProofAutoFunctionFilter,
        LedgerProofFunctionFilter,
    )
except ImportError:  # pragma: no cover
    LedgerProofFunctionFilter = None  # type: ignore[assignment]
    LedgerProofAutoFunctionFilter = None  # type: ignore[assignment]

__all__ = [
    "LedgerProofChatService",
    "LedgerProofFunctionFilter",
    "LedgerProofAutoFunctionFilter",
    "lpr_track",
    "emit_receipt",
    "LogEmitter",
    "QueueEmitter",
    "WebhookEmitter",
    "BaseEmitter",
    "Ed25519Signer",
    "BaseSigner",
    "ChatbotSessionReceipt",
    "GeneratedContentReceipt",
    "AgentFunctionInvocationReceipt",
    "AzureEnterpriseSessionReceipt",
    "SCHEMAS",
    "get_schema",
    "__version__",
]
