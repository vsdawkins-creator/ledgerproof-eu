"""ledgerproof-llamaindex — Article 50 transparency receipts for LlamaIndex.

Public API:
    LedgerProofCallbackHandler — drop into llama_index.core.callbacks.CallbackManager.
    Ed25519Signer              — signing primitive (ephemeral; HSM-backed in production).
    LogEmitter / WebhookEmitter / QueueEmitter — side-channel receipt sinks (C7).
    RagChatbotSessionReceipt / GeneratedContentReceipt / RagSynthesizedResponseReceipt
                               — Pydantic v2 schemas for Article 50 evidence.

Discipline:
    C1 — no claim of regulator endorsement or Article 40 presumption of conformity.
    C4 — adapter does not phone home to LedgerProof servers in normal operation.
    C6 — stream-aware signing; transcript hash committed on event start, signed on event end.
    C7 — side-channel emission only; LlamaIndex response payload is never mutated.
"""

from .callback_handler import LedgerProofCallbackHandler
from .emitter import Emitter, LogEmitter, QueueEmitter, WebhookEmitter
from .schema import (
    GeneratedContentReceipt,
    RagChatbotSessionReceipt,
    RagSynthesizedResponseReceipt,
)
from .signer import Ed25519Signer
from .version import __version__

__all__ = [
    "LedgerProofCallbackHandler",
    "Ed25519Signer",
    "Emitter",
    "LogEmitter",
    "WebhookEmitter",
    "QueueEmitter",
    "RagChatbotSessionReceipt",
    "GeneratedContentReceipt",
    "RagSynthesizedResponseReceipt",
    "__version__",
]
