"""Ed25519 signer for LedgerProof receipts.

MVP: generates an ephemeral in-memory keypair on construction. Suitable for
local development, tests, and demo deployments only.

Phase 4 (production): swap in HSM-backed signing. The `BaseSigner` interface
is stable; HSM backends only need to implement `sign(message: bytes) -> bytes`
and `public_key_bytes() -> bytes`.

Planned production backends (stubs only here, not implemented in MVP):
    - AwsKmsSigner       (boto3 + AWS KMS asymmetric keys)
    - GcpKmsSigner       (google-cloud-kms)
    - AzureKeyVaultSigner (azure-keyvault-keys)
    - YubiHsmSigner      (yubihsm package)
"""

from __future__ import annotations

import base64
from abc import ABC, abstractmethod

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


class BaseSigner(ABC):
    """Common signer interface. Production HSM backends implement this."""

    @abstractmethod
    def sign(self, message: bytes) -> bytes:
        """Return a 64-byte Ed25519 signature over `message`."""

    @abstractmethod
    def public_key_bytes(self) -> bytes:
        """Return the 32-byte raw Ed25519 public key."""

    def public_key_b64(self) -> str:
        """Return the public key as URL-safe base64 (no padding)."""
        return base64.urlsafe_b64encode(self.public_key_bytes()).rstrip(b"=").decode("ascii")


class Ed25519Signer(BaseSigner):
    """Ephemeral in-memory Ed25519 signer.

    A new keypair is generated each time this class is instantiated unless a
    private key is supplied. The private key never leaves memory.

    This is the MVP signer. For production, use an HSM-backed BaseSigner.
    """

    def __init__(self, private_key: Ed25519PrivateKey | None = None) -> None:
        self._private_key: Ed25519PrivateKey = private_key or Ed25519PrivateKey.generate()
        self._public_key: Ed25519PublicKey = self._private_key.public_key()

    def sign(self, message: bytes) -> bytes:
        if not isinstance(message, (bytes, bytearray)):
            raise TypeError("sign() requires bytes")
        return self._private_key.sign(bytes(message))

    def public_key_bytes(self) -> bytes:
        return self._public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

    @classmethod
    def from_seed(cls, seed: bytes) -> "Ed25519Signer":
        """Construct a signer from a 32-byte Ed25519 seed (test fixtures only)."""
        if len(seed) != 32:
            raise ValueError("Ed25519 seed must be exactly 32 bytes")
        priv = Ed25519PrivateKey.from_private_bytes(seed)
        return cls(private_key=priv)


# --- Phase 4 HSM backend stubs (do not import, not implemented) -------------
#
# class AwsKmsSigner(BaseSigner):
#     def __init__(self, key_id: str, region: str): ...
#     def sign(self, message): ...
#     def public_key_bytes(self): ...
#
# class GcpKmsSigner(BaseSigner):
#     def __init__(self, key_resource_name: str): ...
#
# class AzureKeyVaultSigner(BaseSigner):
#     def __init__(self, vault_url: str, key_name: str): ...
#
# class YubiHsmSigner(BaseSigner):
#     def __init__(self, connector_url: str, auth_key_id: int, key_id: int): ...
