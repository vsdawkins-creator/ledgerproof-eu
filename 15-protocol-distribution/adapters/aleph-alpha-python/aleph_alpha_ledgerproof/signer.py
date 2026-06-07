"""Ephemeral Ed25519 signing and local verification (C4)."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any, Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from .canonical import canonicalize


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def _unb64(data: str) -> bytes:
    return base64.b64decode(data.encode("ascii"))


@dataclass(slots=True)
class _PubKeyMaterial:
    raw: bytes

    @property
    def b64(self) -> str:
        return _b64(self.raw)


class EphemeralEd25519Signer:
    """Generates a fresh Ed25519 key per signer instance.

    The protocol deliberately discourages long-lived signing keys for the
    open-source MVP; production deployments are expected to swap in an
    HSM- or KMS-backed signer that conforms to the same `sign(bytes) -> bytes`
    contract.
    """

    def __init__(self) -> None:
        self._sk: Ed25519PrivateKey = Ed25519PrivateKey.generate()
        self._pk: Ed25519PublicKey = self._sk.public_key()

    @property
    def public_key_b64(self) -> str:
        from cryptography.hazmat.primitives import serialization

        raw = self._pk.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        return _b64(raw)

    def sign(self, message: bytes) -> bytes:
        return self._sk.sign(message)

    def sign_canonical(self, payload: Mapping[str, Any]) -> tuple[bytes, bytes]:
        """Return ``(canonical_bytes, signature)``."""
        canon = canonicalize(payload)
        return canon, self.sign(canon)


def verify_receipt(receipt: Mapping[str, Any]) -> bool:
    """Verify a receipt produced by this adapter — purely local (C4).

    The expected receipt shape::

        {
          "protocol": "lpr/1",
          "payload":  { ... schema body ... },
          "sig":      "<base64 ed25519 signature over canonicalize(payload)>",
          "pubkey":   "<base64 raw ed25519 public key>"
        }
    """
    try:
        payload = receipt["payload"]
        sig = _unb64(receipt["sig"])
        pubkey_raw = _unb64(receipt["pubkey"])
    except (KeyError, TypeError, ValueError):
        return False

    try:
        pubkey = Ed25519PublicKey.from_public_bytes(pubkey_raw)
    except Exception:
        return False

    canon = canonicalize(payload)
    try:
        pubkey.verify(sig, canon)
    except InvalidSignature:
        return False
    return True
