"""LedgerProof side-channel adapter for the Aleph Alpha Python SDK.

C1: Independent of any regulator. No Article 40 presumption claim.
C4: Local verification only.
C6: Stream-aware incremental SHA-256.
C7: Side-channel emission — response payload is never modified.
"""

from .version import __version__, PROTOCOL_VERSION
from .client_wrapper import LedgerProofAlephAlpha
from .async_client_wrapper import LedgerProofAsyncAlephAlpha
from .decorator import lpr_track
from .manual import emit_receipt
from .emitter import (
    Emitter,
    StdoutEmitter,
    InMemoryEmitter,
    CallableEmitter,
)
from .signer import EphemeralEd25519Signer, verify_receipt
from .schema import (
    ChatbotSessionV1,
    GeneratedContentV1,
    OnPremSovereignDeploymentV1,
    Article50Scope,
)

__all__ = [
    "__version__",
    "PROTOCOL_VERSION",
    "LedgerProofAlephAlpha",
    "LedgerProofAsyncAlephAlpha",
    "lpr_track",
    "emit_receipt",
    "Emitter",
    "StdoutEmitter",
    "InMemoryEmitter",
    "CallableEmitter",
    "EphemeralEd25519Signer",
    "verify_receipt",
    "ChatbotSessionV1",
    "GeneratedContentV1",
    "OnPremSovereignDeploymentV1",
    "Article50Scope",
]
