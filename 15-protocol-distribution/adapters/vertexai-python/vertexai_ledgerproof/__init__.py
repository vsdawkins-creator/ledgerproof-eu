"""ledgerproof-vertexai — LedgerProof adapter for Google Cloud Vertex AI.

Open cryptographic protocol for EU AI Act Article 50 transparency
receipts. Not endorsed by Google Cloud. Not endorsed by any regulator.
See README for the full C1 disclaimer.
"""
from __future__ import annotations

from . import manual
from .chat_wrapper import LedgerProofChatSession
from .decorator import lpr_track
from .emitter import configure, emit_receipt, get_config
from .manual import emit as emit_manual
from .model_wrapper import LedgerProofGenerativeModel
from .schema import (
    SCHEMA_NAMES,
    ChatbotSessionReceipt,
    EuDataResidencyReceipt,
    GeminiFunctionCallReceipt,
    GeneratedContentReceipt,
    VertexContext,
)
from .signer import EphemeralEd25519Signer, GcpKmsEd25519Signer, Signature
from .version import PROTOCOL_VERSION, __version__

__all__ = [
    "__version__",
    "PROTOCOL_VERSION",
    "SCHEMA_NAMES",
    "LedgerProofGenerativeModel",
    "LedgerProofChatSession",
    "lpr_track",
    "configure",
    "get_config",
    "emit_receipt",
    "emit_manual",
    "manual",
    "VertexContext",
    "ChatbotSessionReceipt",
    "GeneratedContentReceipt",
    "EuDataResidencyReceipt",
    "GeminiFunctionCallReceipt",
    "EphemeralEd25519Signer",
    "GcpKmsEd25519Signer",
    "Signature",
]
