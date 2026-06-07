"""
Ed25519 signer for LedgerProof receipts.

MVP uses an ephemeral in-process key. Production deployments — especially Bedrock
users who already operate within AWS — will typically want HSM-backed signing
via AWS KMS. The `AwsKmsEd25519Signer` stub below documents the intended shape
in detail so deployers can wire it up against their KMS keys without rewriting
the rest of the pipeline. The same `Signer` protocol covers GCP KMS, Azure Key
Vault, and YubiHSM implementations.

NOTE: AWS KMS supports several signing algorithms (ECDSA P-256/P-384/P-521,
RSASSA-PKCS1-v1_5, RSASSA-PSS). KMS does NOT directly expose Ed25519 signing
in many regions today (2026 status). Deployers have two options:
  (a) Use the KMS-native ECDSA algorithm and switch the receipt's
      `signature_alg` to "ecdsa-p256-sha256" — the canonical CBOR payload is
      identical, only the verifier branch differs.
  (b) Use KMS to wrap/unwrap an Ed25519 key stored in an EC2 / Lambda execution
      role and sign in-memory with cryptography. The ephemeral-key model in
      this MVP is the first step toward option (b).
The stub below sketches option (a); see comments inline.
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

    def __init__(
        self,
        private_key: Ed25519PrivateKey | None = None,
        key_id: str | None = None,
    ):
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
    """
    Stub for AWS KMS-backed signing.

    Intended production shape (option (a) from the module docstring):

        import boto3
        kms = boto3.client("kms", region_name="eu-west-1")

        # KMS key created as:
        #   aws kms create-key \
        #     --key-usage SIGN_VERIFY \
        #     --customer-master-key-spec ECC_NIST_P256
        #   (Ed25519 native KMS keys are not yet GA in all regions; ECDSA P256
        #    is the closest stable equivalent. Verifier branch changes
        #    accordingly — see signed_receipt["signature_alg"].)

        def sign(self, message: bytes) -> bytes:
            resp = kms.sign(
                KeyId=self.key_arn,
                Message=message,
                MessageType="RAW",
                SigningAlgorithm="ECDSA_SHA_256",
            )
            return resp["Signature"]

        def public_key_bytes(self) -> bytes:
            resp = kms.get_public_key(KeyId=self.key_arn)
            return resp["PublicKey"]  # SubjectPublicKeyInfo DER

    The MVP intentionally does NOT implement this. Deployers who need KMS today
    should subclass `Signer` and pass their own implementation to
    `LedgerProofBedrockClient(signer=...)`. The canonical CBOR payload signed
    by KMS is byte-identical to what the ephemeral Ed25519 signer produces, so
    verification continues to work offline (constraint C4) with a swapped
    `signature_alg` field.
    """

    def __init__(self, key_arn: str):
        if not key_arn.startswith("arn:aws:kms:"):
            # Soft warning only — KMS key IDs can also be raw UUIDs or aliases.
            pass
        self.key_arn = key_arn

    def sign(self, message: bytes) -> bytes:  # pragma: no cover
        raise NotImplementedError(
            "AWS KMS signer is a documented stub in 0.1.0. "
            "See the module docstring for the production wiring pattern."
        )

    def public_key_bytes(self) -> bytes:  # pragma: no cover
        raise NotImplementedError(
            "AWS KMS signer is a documented stub in 0.1.0. "
            "Call kms.get_public_key(KeyId=self.key_arn) in your implementation."
        )

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
