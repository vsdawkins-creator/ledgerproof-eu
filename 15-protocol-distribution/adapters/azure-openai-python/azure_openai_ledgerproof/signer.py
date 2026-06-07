"""Ed25519 signer + Azure Key Vault stub.

MVP uses an ephemeral in-process Ed25519 key. Production Azure deployments
should plug in `AzureKeyVaultSigner` (stubbed here) and publish the public key
through the Foundation's key registry.
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


class AzureKeyVaultSigner:
    """Stub for Azure Key Vault-backed Ed25519 / EC signer.

    Azure Key Vault (Premium tier, HSM-backed) supports EC keys (P-256 /
    P-384 / P-521). A concrete implementation will:

    1. Accept a Key Vault URL and key name (or full key identifier URL).
    2. Use `azure.identity.DefaultAzureCredential` to authenticate.
    3. Use `azure.keyvault.keys.crypto.CryptographyClient.sign()` to sign
       the canonical CBOR receipt bytes.
    4. Cache the public key bytes after first fetch.

    Concrete implementation lands in v0.2 under
    `ledgerproof-azure-openai[keyvault]`.
    """

    def __init__(
        self,
        vault_url: str,
        key_name: str,
        *,
        key_version: str | None = None,
        credential: object | None = None,
    ) -> None:
        self.vault_url = vault_url
        self.key_name = key_name
        self.key_version = key_version
        self._credential = credential

    def sign(self, message: bytes) -> bytes:  # pragma: no cover
        raise NotImplementedError(
            "AzureKeyVaultSigner is a stub. Install the keyvault extra and "
            "wait for v0.2, or subclass and provide your own implementation "
            "wired to azure.keyvault.keys.crypto.CryptographyClient."
        )

    def public_key_bytes(self) -> bytes:  # pragma: no cover
        raise NotImplementedError(
            "AzureKeyVaultSigner is a stub. See sign() for details."
        )


# Legacy alias retained for cross-adapter consistency with the OpenAI adapter.
HSMSigner = AzureKeyVaultSigner
