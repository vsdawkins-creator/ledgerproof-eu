"""ledgerproof-haystack — LedgerProof adapter for Haystack 2.x.

LedgerProof Foundation (Stichting LedgerProof). Apache 2.0.

Disclaimer (C1): this package does not constitute legal advice,
does not assert presumption of conformity under Article 40 of
Regulation (EU) 2024/1689, and is not endorsed by any regulator.
"""

from .callbacks import StreamingReceiptBuilder, lpr_pipeline_callback
from .canonical import canonical_cbor, hash_payload, merkle_root, sha256_hex
from .components import LedgerProofComponent
from .emitter import (
    CallableEmitter,
    Emitter,
    FileEmitter,
    JSONLEmitter,
    MemoryEmitter,
)
from .schema import (
    SCHEMAS,
    EditorialPipelineReviewV1,
    GeneratedContentV1,
    HaystackNodeReceiptV1,
    RagPipelineSessionV1,
    build_receipt,
    get_schema,
)
from .signer import (
    SigningKey,
    generate_signing_key,
    load_or_generate_signing_key,
    load_signing_key_from_path,
    save_signing_key_to_path,
    verify_signature,
)
from .version import ADAPTER_NAME, PROTOCOL_VERSION, __version__
from .wrappers import LedgerProofGeneratorWrapper

__all__ = [
    "__version__",
    "PROTOCOL_VERSION",
    "ADAPTER_NAME",
    # components
    "LedgerProofComponent",
    "LedgerProofGeneratorWrapper",
    # streaming
    "StreamingReceiptBuilder",
    "lpr_pipeline_callback",
    # schemas
    "SCHEMAS",
    "RagPipelineSessionV1",
    "GeneratedContentV1",
    "HaystackNodeReceiptV1",
    "EditorialPipelineReviewV1",
    "build_receipt",
    "get_schema",
    # signing
    "SigningKey",
    "generate_signing_key",
    "load_or_generate_signing_key",
    "load_signing_key_from_path",
    "save_signing_key_to_path",
    "verify_signature",
    # canonical
    "canonical_cbor",
    "hash_payload",
    "merkle_root",
    "sha256_hex",
    # emitters
    "Emitter",
    "FileEmitter",
    "JSONLEmitter",
    "MemoryEmitter",
    "CallableEmitter",
]
