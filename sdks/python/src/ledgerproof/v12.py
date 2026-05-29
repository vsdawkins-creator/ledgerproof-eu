"""LPR 1.2 canonicality SDK methods.

Importable as `from ledgerproof import v12` once the v1.2 release ships.
Until then this module is forward-looking scaffolding.

Spec reference: 04-lpr-spec/LPR-1.2-CANONICALITY-ANNEX.md
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Sequence
from uuid import UUID


# ──────────────────────────────────────────────────────────────────────
# §3 Lineage chains
# ──────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ChainEntry:
    receipt_id: UUID
    issuer_did: str
    lineage_position: int
    previous_receipt_id: Optional[UUID]
    anchor_status: str
    anchor_block_height: Optional[int]
    identity_verification_level: str
    supersedes: bool
    issued_at: datetime


@dataclass(frozen=True)
class ChainHistory:
    chain_root_id: UUID
    entries: list[ChainEntry]


class CanonicalityMixin:
    """Mixin added to LedgerProofClient in v1.2."""

    # ── §3 Lineage chains ──────────────────────────────────────────────

    def publish_with_predecessor(
        self,
        content: bytes,
        *,
        previous_receipt_id: UUID,
        supersedes: bool = True,
        **kwargs,
    ):
        """Publish an entry that extends an existing chain.

        SDK auto-fetches predecessor's chain_root_id and lineage_position
        from the operator, then submits the new entry with the correct
        chain metadata.

        Args:
            content: Bytes to anchor.
            previous_receipt_id: UUID of the predecessor receipt.
                Must be owned by the same issuer_did, OR a valid
                identity_delegation must exist.
            supersedes: If True (default), the predecessor is deprecated.
                If False, the new entry coexists as a parallel version.

        Raises:
            ChainError: Any of LPR 1.2 §3.3 validation rules failed.
        """
        raise NotImplementedError("Ships with LPR 1.2 (Ticket #9)")

    def get_chain_history(self, receipt_id: UUID) -> ChainHistory:
        """Walk a chain backward to its root.

        GET /v1/chains/{receipt_id}/history
        """
        raise NotImplementedError("Ships with LPR 1.2 (Ticket #9)")

    def get_chain_canonical_head(self, chain_root_id: UUID) -> ChainEntry:
        """Return the current canonical head of a chain.

        GET /v1/chains/{chain_root_id}/canonical
        """
        raise NotImplementedError("Ships with LPR 1.2 (Ticket #9)")

    def delegate_chain(
        self,
        *,
        chain_root_id: UUID,
        delegate_did: str,
        expires_at: datetime,
        supersession_allowed: bool = False,
    ):
        """Authorize another DID to extend a chain you own.

        See LPR 1.2 §3.5.
        """
        raise NotImplementedError("Ships with LPR 1.2 (Ticket #8)")

    # ── §4 Similarity hashing ──────────────────────────────────────────

    def find_similar(
        self,
        *,
        content: Optional[bytes] = None,
        similarity_hash: Optional[dict] = None,
        content_type: str = "text/plain",
        threshold: int = 30,
        limit: int = 5,
    ) -> list[dict]:
        """Search for near-duplicate receipts.

        POST /v1/similarity/search
        """
        raise NotImplementedError("Ships with LPR 1.2 (Ticket #14)")

    # ── §5 Witness attestation ─────────────────────────────────────────

    def attest_receipt(
        self,
        *,
        target_receipt_id: UUID,
        attestation_type: str,
        signer_did: str,
        signer_key: bytes,
        statement: Optional[str] = None,
    ) -> UUID:
        """Counter-sign an existing receipt.

        attestation_type ∈ {co-sign, witness, notary, regulator, publisher, received}
        See LPR 1.2 §5.

        Returns:
            UUID of the new attestation entry.
        """
        raise NotImplementedError("Ships with LPR 1.2 (Ticket #23)")

    def list_attestations(self, receipt_id: UUID, *, include_revoked: bool = False):
        """List attestations on a receipt."""
        raise NotImplementedError("Ships with LPR 1.2 (Ticket #23)")

    def revoke_attestation(
        self,
        *,
        attestation_id: UUID,
        revoker_did: str,
        revoker_key: bytes,
        rationale: str,
    ) -> UUID:
        """Revoke one of your own attestations."""
        raise NotImplementedError("Ships with LPR 1.2 (Ticket #23)")

    # ── §6 Canonical claims ────────────────────────────────────────────

    def claim_canonical(
        self,
        *,
        receipt_id: UUID,
        statement: str,
        evidence_receipt_ids: Sequence[UUID] = (),
    ) -> UUID:
        """Assert that a receipt you own is canonical for its content.

        Triggers a 30-day dispute window.
        """
        raise NotImplementedError("Ships with LPR 1.2 (Ticket #30)")

    def dispute_canonical_claim(
        self,
        *,
        claim_id: UUID,
        competing_receipt_id: UUID,
        rationale: str,
        evidence_receipt_ids: Sequence[UUID] = (),
    ) -> UUID:
        """Dispute someone else's canonical claim with a competing receipt.

        Triggers a 30-day Foundation arbitration window.
        """
        raise NotImplementedError("Ships with LPR 1.2 (Ticket #30)")


# ──────────────────────────────────────────────────────────────────────
# Errors mirror the Rust LPR12XX_ error codes.
# ──────────────────────────────────────────────────────────────────────


class CanonicalityError(Exception):
    """Base class for all LPR 1.2 canonicality errors."""

    code: str = ""


class ChainError(CanonicalityError):
    """LPR12{00-08}: lineage chain validation failures."""


class SimilarityError(CanonicalityError):
    """LPR12{10-12}: similarity hash failures."""


class AttestationError(CanonicalityError):
    """LPR12{20-25}: attestation validation failures."""


class CanonicalRegistryError(CanonicalityError):
    """LPR12{30-36}: canonical registry state-machine failures."""
