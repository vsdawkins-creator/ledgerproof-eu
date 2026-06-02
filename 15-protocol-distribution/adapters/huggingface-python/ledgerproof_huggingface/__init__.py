"""ledgerproof-huggingface — Article 50 transparency receipts for Hugging Face.

Covers both:
  * `huggingface_hub.InferenceClient` / `AsyncInferenceClient` — hosted
    Inference API (Hugging Face is EU-headquartered: Paris / NYC).
  * `transformers.Pipeline` — local / self-hosted inference for on-prem
    deployers.

This package emits signed receipts on a side channel. It does **not** modify
the Hugging Face response. It does **not** phone home. It does **not** claim
regulator endorsement, Article 40 presumption of conformity, or any
endorsement by Hugging Face. See the discipline section of the README.
"""

from .async_inference_wrapper import LedgerProofAsyncInferenceClient
from .canonical import canonical_encode, canonical_hash, canonical_hash_hex
from .decorator import lpr_track
from .emitter import Emitter, LogEmitter, QueueEmitter, WebhookEmitter
from .inference_client_wrapper import LedgerProofInferenceClient
from .manual import emit_receipt
from .pipeline_wrapper import LedgerProofPipeline
from .schema import (
    SCHEMAS,
    ChatbotSessionV1,
    EUOpenModelHostedV1,
    GeneratedContentV1,
    LocalInferenceV1,
    build_receipt,
)
from .signer import Ed25519Signer, HSMSigner, Signer
from .version import __version__

__all__ = [
    "__version__",
    # Clients
    "LedgerProofInferenceClient",
    "LedgerProofAsyncInferenceClient",
    "LedgerProofPipeline",
    # Patterns
    "lpr_track",
    "emit_receipt",
    # Schemas
    "ChatbotSessionV1",
    "GeneratedContentV1",
    "EUOpenModelHostedV1",
    "LocalInferenceV1",
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
