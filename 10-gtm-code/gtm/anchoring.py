"""LedgerProof Receipt anchoring for outbound artifacts.

Dogfood: every outbound the Foundation produces is anchored as a LedgerProof
Receipt. This module presents one interface; backends:

- `RealBackend`: uses the published `ledgerproof` Python SDK (1.1+)
- `MockBackend`: deterministic hash-based receipt IDs for dev + CI

The real backend activates when LPR_API_KEY is in env. The mock backend
REFUSES to run when LPR_ENV=prod to prevent accidental fake anchors in
production.
"""

from __future__ import annotations

import hashlib
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class ReceiptHandle:
    receipt_id: str
    bitcoin_block: int | None
    anchor_status: str
    issued_at: datetime
    backend: str

    @property
    def is_mock(self) -> bool:
        return self.backend == "mock"


class AnchoringBackend(ABC):
    @abstractmethod
    def issue(
        self,
        *,
        artifact_slug: str,
        body: str,
        article50_subclause: str | None,
        profile: str,
    ) -> ReceiptHandle: ...


class MockBackend(AnchoringBackend):
    """Deterministic mock for dev + CI. Never produces a real anchor."""

    def __init__(self) -> None:
        if os.environ.get("LPR_ENV") == "prod":
            raise RuntimeError(
                "MockBackend refuses to run in LPR_ENV=prod; set LPR_API_KEY"
            )

    def issue(
        self,
        *,
        artifact_slug: str,
        body: str,
        article50_subclause: str | None,
        profile: str,
    ) -> ReceiptHandle:
        digest = hashlib.sha256(
            f"{artifact_slug}|{profile}|{article50_subclause or ''}|{body}".encode()
        ).hexdigest()
        return ReceiptHandle(
            receipt_id=f"mock-{digest[:16]}",
            bitcoin_block=None,
            anchor_status="mock",
            issued_at=datetime.now(tz=timezone.utc),
            backend="mock",
        )


class RealBackend(AnchoringBackend):
    """Wraps the published ledgerproof SDK."""

    def __init__(self, api_key: str) -> None:
        try:
            import ledgerproof  # type: ignore
        except ImportError as e:
            raise RuntimeError(
                "ledgerproof SDK not installed; `pip install 'lpr-gtm[real]'`"
            ) from e
        self._client = ledgerproof.Client(api_key=api_key)

    def issue(
        self,
        *,
        artifact_slug: str,
        body: str,
        article50_subclause: str | None,
        profile: str,
    ) -> ReceiptHandle:
        output_hash = hashlib.sha256(body.encode()).hexdigest()
        receipt = self._client.issue(
            output_hash=output_hash,
            output_type="text",
            issuer_did="did:web:foundation.ledgerproofhq.io",
            article50_subclause=article50_subclause,
            profile=profile,
            system_metadata={"artifact_slug": artifact_slug},
        )
        return ReceiptHandle(
            receipt_id=receipt.receipt_id,
            bitcoin_block=receipt.anchor_block,
            anchor_status=receipt.anchor_status,
            issued_at=datetime.now(tz=timezone.utc),
            backend="real",
        )


def default_backend() -> AnchoringBackend:
    api_key = os.environ.get("LPR_API_KEY")
    if api_key:
        return RealBackend(api_key=api_key)
    return MockBackend()
