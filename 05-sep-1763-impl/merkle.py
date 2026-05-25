"""
RFC 6962 Merkle tree construction with domain separation.

Used for daily aggregation of LPR receipts before anchoring to Bitcoin OP_RETURN.

The domain separation (0x00 for leaves, 0x01 for internal nodes) is mandatory
under RFC 6962 §2.1 and LPR 1.0 §5.2 — it prevents second-preimage attacks
where an attacker swaps a leaf for an internal-node concatenation.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass


def leaf_hash(data: bytes) -> bytes:
    """RFC 6962 leaf hash: SHA-256(0x00 || data)."""
    return hashlib.sha256(b"\x00" + data).digest()


def node_hash(left: bytes, right: bytes) -> bytes:
    """RFC 6962 internal-node hash: SHA-256(0x01 || left || right)."""
    return hashlib.sha256(b"\x01" + left + right).digest()


@dataclass
class MerkleTree:
    """A simple in-memory Merkle tree following the RFC 6962 construction."""

    leaves: list[bytes]

    def root(self) -> bytes:
        """Compute and return the Merkle root over the current leaves."""
        if not self.leaves:
            return hashlib.sha256(b"").digest()
        return _root(self.leaves)

    def inclusion_proof(self, leaf_index: int) -> list[bytes]:
        """Return the inclusion proof path for the leaf at the given index."""
        if leaf_index < 0 or leaf_index >= len(self.leaves):
            raise IndexError(f"leaf_index {leaf_index} out of range (0..{len(self.leaves)-1})")
        return _inclusion_proof(self.leaves, leaf_index)


def verify_inclusion(
    leaf: bytes,
    leaf_index: int,
    tree_size: int,
    proof: list[bytes],
    root: bytes,
) -> bool:
    """Verify an inclusion proof against a known root. Returns True iff valid."""
    if leaf_index < 0 or leaf_index >= tree_size:
        return False
    fn = leaf_index
    sn = tree_size - 1
    r = leaf
    for sibling in proof:
        if sn == 0:
            return False
        if fn % 2 == 1 or fn == sn:
            r = node_hash(sibling, r)
            while fn % 2 == 0:
                fn >>= 1
                sn >>= 1
        else:
            r = node_hash(r, sibling)
        fn >>= 1
        sn >>= 1
    return r == root and sn == 0


# ---- internal -----


def _root(leaves: list[bytes]) -> bytes:
    if len(leaves) == 1:
        return leaves[0]
    k = _largest_power_of_two_less_than(len(leaves))
    return node_hash(_root(leaves[:k]), _root(leaves[k:]))


def _inclusion_proof(leaves: list[bytes], m: int) -> list[bytes]:
    n = len(leaves)
    if n == 1:
        return []
    k = _largest_power_of_two_less_than(n)
    if m < k:
        return _inclusion_proof(leaves[:k], m) + [_root(leaves[k:])]
    return _inclusion_proof(leaves[k:], m - k) + [_root(leaves[:k])]


def _largest_power_of_two_less_than(n: int) -> int:
    """Largest power of 2 strictly less than n (n > 1)."""
    k = 1
    while (k << 1) < n:
        k <<= 1
    return k
