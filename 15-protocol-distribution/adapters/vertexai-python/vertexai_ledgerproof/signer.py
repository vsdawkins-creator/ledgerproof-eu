"""Ed25519 receipt signer.

Phase 1 MVP uses an ephemeral in-process Ed25519 key generated per signer
instance. The public key is included in every receipt so verifiers can
check signatures without an out-of-band key distribution step.

Phase 2 (post-MVP) will support:
- GCP Cloud KMS-backed signing keys (CryptoKeyVersionAlgorithm: EC_SIGN_ED25519
  or asymmetric sign via HSM). The signer interface here is intentionally
  designed so a `KmsEd25519Signer` can be slotted in without changing
  emitter or model wrapper code. The expected GCP KMS resource path format
  is:
      projects/{p}/locations/{loc}/keyRings/{ring}/cryptoKeys/{key}/cryptoKeyVersions/{v}
  Co-locating the KMS keyring with the Vertex AI inference region (e.g.
  europe-west4) is the recommended pattern for EU data residency receipts.
- AWS KMS / Azure Key Vault analogues
- Hardware token (PKCS#11)
"""
from __future__ import annotations

import base64
from dataclasses import dataclass

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives import serialization


@dataclass(frozen=True)
class Signature:
    """An Ed25519 signature bundle."""

    public_key_b64: str
    signature_b64: str
    algorithm: str = "Ed25519"


class EphemeralEd25519Signer:
    """In-process Ed25519 signer.

    Generates a fresh key on construction. Not suitable for production
    receipts that must be cross-checked across processes — use the
    forthcoming KMS-backed signer for that.
    """

    def __init__(self) -> None:
        self._sk: Ed25519PrivateKey = Ed25519PrivateKey.generate()
        self._pk: Ed25519PublicKey = self._sk.public_key()

    @property
    def public_key_bytes(self) -> bytes:
        return self._pk.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

    @property
    def public_key_b64(self) -> str:
        return base64.b64encode(self.public_key_bytes).decode("ascii")

    def sign(self, message: bytes) -> Signature:
        sig = self._sk.sign(message)
        return Signature(
            public_key_b64=self.public_key_b64,
            signature_b64=base64.b64encode(sig).decode("ascii"),
        )


# ---- KMS placeholder ----------------------------------------------------


class GcpKmsEd25519Signer:  # pragma: no cover — Phase 2
    """Stub for GCP Cloud KMS-backed Ed25519 signer (Phase 2).

    Will use ``google-cloud-kms`` (``KeyManagementServiceClient.asymmetric_sign``)
    with an Ed25519 keyring co-located with the Vertex AI inference region.
    """

    def __init__(self, key_resource: str) -> None:
        self.key_resource = key_resource
        raise NotImplementedError(
            "GcpKmsEd25519Signer is reserved for Phase 2. Use "
            "EphemeralEd25519Signer for the MVP."
        )
