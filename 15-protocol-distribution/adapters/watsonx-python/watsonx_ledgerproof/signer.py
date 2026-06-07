"""
Ed25519 signer for LedgerProof receipts.

MVP uses an ephemeral in-process key. IBM enterprise deployers — who are
typically operating in IBM Cloud and have access to IBM Key Protect or IBM
Cloud Hyper Protect Crypto Services (HPCS, FIPS 140-2 Level 4) — will want
HSM-backed signing in production.

The `IbmKeyProtectEd25519Signer` and `IbmHpcsEd25519Signer` stubs document the
intended production shapes. The canonical CBOR payload signed by an HSM is
byte-identical to what the ephemeral signer produces, so the verifier branch
only differs by signature algorithm.
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


class IbmKeyProtectEd25519Signer:
    """
    Stub for IBM Key Protect-backed signing.

    Production shape (sketch):

        from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
        from ibm_key_protect_api.v2 import IbmKeyProtectApiV2

        authenticator = IAMAuthenticator(apikey=...)
        kp = IbmKeyProtectApiV2(authenticator=authenticator)
        kp.set_service_url("https://eu-de.kms.cloud.ibm.com")

        def sign(self, message: bytes) -> bytes:
            # IBM Key Protect (standard tier) supports envelope encryption but
            # NOT generic message signing directly. For Ed25519 signing inside
            # IBM Cloud, customers should use IBM Cloud Hyper Protect Crypto
            # Services (HPCS, FIPS 140-2 Level 4) via GREP11 / PKCS#11.
            raise NotImplementedError

    The 0.1.0 MVP does NOT implement this. Deployers who need EU-DE HSM-backed
    signing today should subclass `Signer` and pass it via
    `LedgerProofModelInference(signer=...)`.
    """

    def __init__(self, key_crn: str):
        # IBM key CRN format:
        # crn:v1:bluemix:public:kms:eu-de:a/<account>:<instance>:key:<key-id>
        self.key_crn = key_crn

    def sign(self, message: bytes) -> bytes:  # pragma: no cover
        raise NotImplementedError(
            "IBM Key Protect signer is a documented stub in 0.1.0. "
            "Standard-tier Key Protect does not expose generic message signing. "
            "Use IBM Cloud Hyper Protect Crypto Services (HPCS) for Ed25519 "
            "signing in EU regions; see IbmHpcsEd25519Signer."
        )

    def public_key_bytes(self) -> bytes:  # pragma: no cover
        raise NotImplementedError(
            "IBM Key Protect signer is a documented stub in 0.1.0."
        )

    @property
    def key_id(self) -> str:
        return self.key_crn


class IbmHpcsEd25519Signer:
    """
    Stub for IBM Cloud Hyper Protect Crypto Services (HPCS) signing via GREP11.

    HPCS is FIPS 140-2 Level 4 certified, EU-DE region available (Frankfurt),
    and exposes a PKCS#11 / GREP11 surface that supports Ed25519 signing.

    Production shape (sketch):

        import grpc, server_pb2, server_pb2_grpc
        # ... HPCS GREP11 client setup ...

        def sign(self, message: bytes) -> bytes:
            # SignSingle with CKM_IBM_ED25519_SHA512 mechanism.
            raise NotImplementedError

    Not implemented in MVP.
    """

    def __init__(self, hpcs_instance_id: str, key_label: str):
        self.hpcs_instance_id = hpcs_instance_id
        self.key_label = key_label

    def sign(self, message: bytes) -> bytes:  # pragma: no cover
        raise NotImplementedError("IBM HPCS signer not implemented in MVP")

    def public_key_bytes(self) -> bytes:  # pragma: no cover
        raise NotImplementedError("IBM HPCS signer not implemented in MVP")

    @property
    def key_id(self) -> str:
        return f"hpcs:{self.hpcs_instance_id}:{self.key_label}"


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
