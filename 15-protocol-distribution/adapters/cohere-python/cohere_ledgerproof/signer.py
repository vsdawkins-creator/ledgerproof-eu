"""
Ed25519 signer for LedgerProof receipts.

MVP uses an ephemeral in-process key. Production deployments will plug HSM-backed
signers (AWS KMS, GCP KMS, YubiHSM, Azure Key Vault) via the same `Signer` protocol.
"""

from __future__ import annotations

import base64
from typing import Protocol, runtime_checkable

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


@runtime_checkable
class Signer(Protocol):
    """A minimal signing interface; HSM-backed implementations satisfy this."""

    def sign(self, message: bytes) -> bytes: ...

    def public_key_bytes(self) -> bytes: ...

    @property
    def key_id(self) -> str: ...


class Ed25519Signer:
    """Ephemeral Ed25519 signer. Suitable for development and MVP only."""

    def __init__(self, private_key: Ed25519PrivateKey | None = None, key_id: str | None = None):
        self._sk = private_key or Ed25519PrivateKey.generate()
        self._key_id = key_id or _fingerprint(self._sk.public_key())

    def sign(self, message: bytes) -> bytes:
        return self._sk.sign(message)

    def public_key_bytes(self) -> bytes:
        return self._sk.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

    def public_key_b64(self) -> str:
        return base64.b64encode(self.public_key_bytes()).decode("ascii")

    @property
    def key_id(self) -> str:
        return self._key_id

    @classmethod
    def from_seed(cls, seed: bytes, key_id: str | None = None) -> "Ed25519Signer":
        if len(seed) != 32:
            raise ValueError("Ed25519 seed must be exactly 32 bytes")
        return cls(Ed25519PrivateKey.from_private_bytes(seed), key_id=key_id)


# ---------------------------------------------------------------------------
# HSM stubs (production wiring lands later)
# ---------------------------------------------------------------------------


class AwsKmsEd25519Signer:
    """Stub for AWS KMS-backed Ed25519 signing. Not implemented in MVP."""

    def __init__(self, key_arn: str):
        self.key_arn = key_arn

    def sign(self, message: bytes) -> bytes:  # pragma: no cover
        raise NotImplementedError("AWS KMS signer not implemented in MVP")

    def public_key_bytes(self) -> bytes:  # pragma: no cover
        raise NotImplementedError("AWS KMS signer not implemented in MVP")

    @property
    def key_id(self) -> str:
        return self.key_arn


class GcpKmsEd25519Signer:
    """Stub for GCP KMS-backed Ed25519 signing. Not implemented in MVP."""

    def __init__(self, key_resource_name: str):
        self.key_resource_name = key_resource_name

    def sign(self, message: bytes) -> bytes:  # pragma: no cover
        raise NotImplementedError("GCP KMS signer not implemented in MVP")

    def public_key_bytes(self) -> bytes:  # pragma: no cover
        raise NotImplementedError("GCP KMS signer not implemented in MVP")

    @property
    def key_id(self) -> str:
        return self.key_resource_name


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fingerprint(pk: Ed25519PublicKey) -> str:
    import hashlib

    raw = pk.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return "lpr-ed25519-" + hashlib.sha256(raw).hexdigest()[:16]


def verify(public_key_bytes: bytes, message: bytes, signature: bytes) -> bool:
    """Offline verification helper (constraint C4)."""
    try:
        pk = Ed25519PublicKey.from_public_bytes(public_key_bytes)
        pk.verify(signature, message)
        return True
    except Exception:
        return False
