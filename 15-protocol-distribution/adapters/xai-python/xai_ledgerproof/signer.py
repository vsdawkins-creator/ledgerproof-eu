"""Ed25519 signer.

MVP uses an ephemeral in-process Ed25519 key. Production deployments should
plug in an HSM-backed signer; see `HSMSigner` stub.
"""

from __future__ import annotations

from typing import Protocol

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


class Signer(Protocol):
    """Signer protocol — any object implementing this is plug-compatible."""

    def sign(self, message: bytes) -> bytes: ...

    def public_key_bytes(self) -> bytes: ...


class Ed25519Signer:
    """Ephemeral Ed25519 signer.

    Generates a fresh keypair on construction unless `private_key_bytes` is
    provided. For MVP / local testing only — production deployers must use
    HSM-backed signing and publish the public key through the Foundation's
    key registry.
    """

    def __init__(self, private_key_bytes: bytes | None = None) -> None:
        if private_key_bytes is None:
            self._key = Ed25519PrivateKey.generate()
        else:
            self._key = Ed25519PrivateKey.from_private_bytes(private_key_bytes)

    def sign(self, message: bytes) -> bytes:
        return self._key.sign(message)

    def public_key_bytes(self) -> bytes:
        pub: Ed25519PublicKey = self._key.public_key()
        return pub.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

    def private_key_bytes(self) -> bytes:
        return self._key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )


class HSMSigner:
    """Stub for HSM-backed signer.

    Concrete implementations (AWS KMS, GCP KMS, Azure Key Vault, YubiHSM2)
    land in v0.2. Subclass and implement `sign` and `public_key_bytes`.
    """

    def __init__(self, key_id: str) -> None:
        self.key_id = key_id

    def sign(self, message: bytes) -> bytes:  # pragma: no cover
        raise NotImplementedError(
            "HSMSigner is a stub. Provide a concrete backend in v0.2."
        )

    def public_key_bytes(self) -> bytes:  # pragma: no cover
        raise NotImplementedError(
            "HSMSigner is a stub. Provide a concrete backend in v0.2."
        )
