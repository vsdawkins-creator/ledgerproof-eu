"""Ed25519 signer for LedgerProof receipts.

MVP ships with an in-process ephemeral keypair. Production deployments MUST
substitute an HSM-backed signer — see ``HsmSignerStub`` for the interface.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


class Signer(Protocol):
    """Minimal interface every signer must implement.

    Keeping this narrow lets us drop in AWS KMS / GCP Cloud HSM / on-prem Luna
    later without changing the callback handler.
    """

    def sign(self, message: bytes) -> bytes: ...

    @property
    def public_key_bytes(self) -> bytes: ...

    @property
    def key_id(self) -> str: ...


@dataclass
class Ed25519Signer:
    """Ed25519 signer backed by an in-process private key.

    Use ``Ed25519Signer.ephemeral()`` for tests / examples. Pass an existing
    ``private_key`` for deterministic test fixtures. For production, do NOT use
    this class directly — wrap an HSM behind the ``Signer`` protocol instead.
    """

    private_key: Ed25519PrivateKey
    _key_id: str = "lpr-ephemeral"

    @classmethod
    def ephemeral(cls, key_id: str = "lpr-ephemeral") -> "Ed25519Signer":
        """Generate a fresh in-memory keypair. Lost on process exit."""
        return cls(private_key=Ed25519PrivateKey.generate(), _key_id=key_id)

    @classmethod
    def from_private_bytes(cls, raw: bytes, key_id: str = "lpr-static") -> "Ed25519Signer":
        """Load a 32-byte Ed25519 seed. For test fixtures only."""
        if len(raw) != 32:
            raise ValueError("Ed25519 seed must be exactly 32 bytes")
        return cls(private_key=Ed25519PrivateKey.from_private_bytes(raw), _key_id=key_id)

    def sign(self, message: bytes) -> bytes:
        if not isinstance(message, (bytes, bytearray)):
            raise TypeError("sign requires bytes")
        return self.private_key.sign(bytes(message))

    @property
    def public_key(self) -> Ed25519PublicKey:
        return self.private_key.public_key()

    @property
    def public_key_bytes(self) -> bytes:
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

    @property
    def key_id(self) -> str:
        return self._key_id


class HsmSignerStub:
    """Placeholder showing the HSM signer surface.

    A real implementation would call (for example) ``kms.sign(KeyId=..., Message=...)``
    on AWS KMS, or the equivalent on GCP Cloud HSM / on-prem Luna / YubiHSM.
    The Foundation will publish a reference HSM signer alongside the v1.0 release.
    """

    def __init__(self, key_id: str):
        self._key_id = key_id

    def sign(self, message: bytes) -> bytes:  # pragma: no cover - stub
        raise NotImplementedError(
            "HsmSignerStub is a placeholder. Implement against your HSM vendor SDK."
        )

    @property
    def public_key_bytes(self) -> bytes:  # pragma: no cover - stub
        raise NotImplementedError

    @property
    def key_id(self) -> str:
        return self._key_id
