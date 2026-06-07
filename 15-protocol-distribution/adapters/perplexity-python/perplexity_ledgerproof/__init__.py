"""ledgerproof-perplexity — Article 50 transparency receipts for Perplexity AI.

Perplexity AI's Sonar family (`sonar`, `sonar-pro`, `sonar-reasoning`,
`sonar-deep-research`) is exposed through an OpenAI-compatible REST API at
`https://api.perplexity.ai`, so this adapter wraps the official `openai`
Python SDK configured for that base URL.

Perplexity's distinguishing surface is **live web search with citations**.
Every Sonar response carries a `citations` field listing the source URLs
that grounded the answer. This adapter auto-extracts those citations and
binds a deterministic hash into the signed receipt — making it directly
useful for Article 50(4) public-interest text labelling, where regulators
will want to verify *which* sources an AI-generated text drew on.

This package emits signed receipts on a side channel. It does **not**
modify the Perplexity response. It does **not** phone home. It does
**not** claim regulator endorsement, Article 40 presumption of
conformity, or Perplexity endorsement. See the discipline section of
the README.
"""

from .async_client_wrapper import LedgerProofAsyncPerplexity
from .canonical import (
    canonical_encode,
    canonical_hash,
    canonical_hash_hex,
    citation_list_hash_hex,
)
from .client_wrapper import (
    PERPLEXITY_DEFAULT_BASE_URL,
    LedgerProofPerplexity,
)
from .decorator import lpr_track
from .emitter import Emitter, LogEmitter, QueueEmitter, WebhookEmitter
from .manual import emit_receipt, extract_citations
from .schema import (
    SCHEMAS,
    AISearchWithCitationsV1,
    ChatbotSessionV1,
    GeneratedContentV1,
    PublicInterestTextV1,
    build_receipt,
)
from .signer import Ed25519Signer, HSMSigner, Signer
from .version import __version__

__all__ = [
    "__version__",
    # Clients
    "LedgerProofPerplexity",
    "LedgerProofAsyncPerplexity",
    "PERPLEXITY_DEFAULT_BASE_URL",
    # Patterns
    "lpr_track",
    "emit_receipt",
    "extract_citations",
    # Schemas
    "ChatbotSessionV1",
    "GeneratedContentV1",
    "AISearchWithCitationsV1",
    "PublicInterestTextV1",
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
    "citation_list_hash_hex",
]
