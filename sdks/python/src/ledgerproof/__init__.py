"""LedgerProof Python SDK — EU AI Act Article 50 cryptographic transparency receipts.

The three-line Article 50 compliance story::

    import openai
    import ledgerproof

    client = openai.OpenAI()
    ledgerproof.attach(
        client,
        publisher_id="LEI:5493001KJTIIGC8Y1R12",
        deployer_country="DE",
        deployer_name="Acme Corp",
    )

    # Every chat completion from here on issues an LPR receipt
    # automatically, Bitcoin-anchored, GDPR-safe, verifiable by any party.

Direct API::

    from ledgerproof import LedgerProof

    lp = LedgerProof(
        publisher_id="LEI:5493001KJTIIGC8Y1R12",
        deployer_country="DE",
    )
    receipt = lp.publish_ai_article_50(
        artifact="The generated article text...",
        artifact_content_type="text/plain",
        ai_system_id="openai/gpt-4o/2024-11-20",
        deployer_name="Acme Insurance AG",
        content_category="SYNTHETIC_TEXT",
    )
    print(receipt.verify_url)

Documentation: https://docs.ledgerproofhq.io/sdks/python
LPR specification: https://github.com/vsdawkins-creator/ledgerproof-eu
"""

from __future__ import annotations

from ._version import __version__
from .adapters import attach, detach
from .canonical import (
    artifact_hash,
    canonical_json,
    content_hash,
    entry_hash,
    sha256_hex,
)
from .client import AsyncLedgerProof, DEFAULT_API_BASE, LedgerProof
from .errors import (
    APIError,
    AuthenticationError,
    ChainError,
    ConfigurationError,
    GDPRSafetyError,
    KeyManagementError,
    LedgerProofError,
    NetworkError,
    RateLimitError,
    ValidationError,
)
from .keys import Keypair
from .types import (
    AiArticle50Content,
    AiChatbotSessionContent,
    AiHumanReviewContent,
    ContentCategory,
    EntryResponse,
    GenerationType,
    NotificationMethod,
    PerceptualHash,
    Receipt,
    ReviewType,
)

__all__ = [
    "APIError",
    "AiArticle50Content",
    "AiChatbotSessionContent",
    "AiHumanReviewContent",
    "AsyncLedgerProof",
    "AuthenticationError",
    "ChainError",
    "ConfigurationError",
    "ContentCategory",
    "DEFAULT_API_BASE",
    "EntryResponse",
    "GDPRSafetyError",
    "GenerationType",
    "KeyManagementError",
    "Keypair",
    "LedgerProof",
    "LedgerProofError",
    "NetworkError",
    "NotificationMethod",
    "PerceptualHash",
    "RateLimitError",
    "Receipt",
    "ReviewType",
    "ValidationError",
    "__version__",
    "artifact_hash",
    "attach",
    "canonical_json",
    "content_hash",
    "detach",
    "entry_hash",
    "sha256_hex",
]
