"""ledgerproof-langchain

LangChain and LangGraph adapter for the LedgerProof protocol. Emits signed
EU AI Act Article 50 transparency receipts as a side channel.

Verification is offline. Receipts are emitted to log/queue/webhook. The LLM
response payload is never modified by this adapter.
"""

from .callback_handler import LedgerProofCallbackHandler
from .emitter import LogEmitter, QueueEmitter, WebhookEmitter, BaseEmitter
from .schema import (
    ChatbotSessionReceipt,
    GeneratedContentReceipt,
    HumanReviewReceipt,
    SCHEMAS,
)
from .signer import Ed25519Signer
from .version import __version__

# LangGraph middleware is optional; import lazily so the base package
# does not hard-require langgraph.
try:
    from .langgraph_middleware import lpr_receipt_node  # noqa: F401
except ImportError:  # pragma: no cover - optional dependency
    lpr_receipt_node = None  # type: ignore[assignment]

__all__ = [
    "LedgerProofCallbackHandler",
    "LogEmitter",
    "QueueEmitter",
    "WebhookEmitter",
    "BaseEmitter",
    "ChatbotSessionReceipt",
    "GeneratedContentReceipt",
    "HumanReviewReceipt",
    "SCHEMAS",
    "Ed25519Signer",
    "lpr_receipt_node",
    "__version__",
]
