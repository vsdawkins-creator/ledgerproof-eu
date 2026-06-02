"""
LedgerProof adapter for the Replicate Python SDK.

Side-channel cryptographic transparency receipts for EU AI Act Article 50 evidence,
covering text, image, audio, and video generation across the Replicate model
ecosystem (Llama, FLUX, Stable Diffusion, Whisper, MusicGen, ZeroScope, ...).

Discipline:
  - C1: No regulator endorsement, no Article 40 presumption of conformity,
        no Replicate endorsement.
  - C4: Offline verification only; no phone-home.
  - C6: Stream-aware SHA-256 over text deltas and binary chunks.
  - C7: Side-channel emission only; never modifies the Replicate response.
"""

from .canonical import (
    IncrementalBytesHasher,
    IncrementalTextHasher,
    canonical_encode,
    canonical_hash,
    hash_bytes,
    hash_stream,
    hash_text,
)
from .client_wrapper import LedgerProofReplicateClient
from .decorator import lpr_track
from .emitter import (
    Emitter,
    LogEmitter,
    MultiEmitter,
    QueueEmitter,
    StderrEmitter,
    WebhookEmitter,
)
from .manual import (
    build_input_refs,
    build_model_ref_from_coordinate,
    build_model_ref_from_prediction,
    emit_receipt,
    hash_audio_bytes,
    hash_file_output,
    hash_image_bytes,
    hash_video_bytes,
    parse_model_coordinate,
)
from .schema import (
    ContentRef,
    InputRef,
    ModelRef,
    OutputArtifactRef,
    ReceiptV1,
    RegulatoryContext,
    build_chatbot_session_receipt,
    build_generated_content_receipt,
    build_multimodel_attribution_receipt,
    build_synthetic_audio_receipt,
    build_synthetic_image_receipt,
    build_synthetic_video_receipt,
)
from .signer import (
    AwsKmsEd25519Signer,
    Ed25519Signer,
    GcpKmsEd25519Signer,
    Signer,
    verify,
)
from .version import __version__

__all__ = [
    "__version__",
    # client wrapper
    "LedgerProofReplicateClient",
    # decorator
    "lpr_track",
    # manual
    "emit_receipt",
    "parse_model_coordinate",
    "build_model_ref_from_coordinate",
    "build_model_ref_from_prediction",
    "build_input_refs",
    "hash_image_bytes",
    "hash_audio_bytes",
    "hash_video_bytes",
    "hash_file_output",
    # schemas
    "ContentRef",
    "InputRef",
    "OutputArtifactRef",
    "ModelRef",
    "ReceiptV1",
    "RegulatoryContext",
    "build_chatbot_session_receipt",
    "build_generated_content_receipt",
    "build_synthetic_image_receipt",
    "build_synthetic_audio_receipt",
    "build_synthetic_video_receipt",
    "build_multimodel_attribution_receipt",
    # canonical
    "canonical_encode",
    "canonical_hash",
    "hash_text",
    "hash_bytes",
    "hash_stream",
    "IncrementalTextHasher",
    "IncrementalBytesHasher",
    # emitters
    "Emitter",
    "LogEmitter",
    "StderrEmitter",
    "WebhookEmitter",
    "QueueEmitter",
    "MultiEmitter",
    # signers
    "Signer",
    "Ed25519Signer",
    "AwsKmsEd25519Signer",
    "GcpKmsEd25519Signer",
    "verify",
]
