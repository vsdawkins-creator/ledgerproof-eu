"""Ed25519 signing for LedgerProof receipts."""

from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Union

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


@dataclass
class SignedReceipt:
    payload_cbor: bytes
    signature: bytes
    public_key_b64: str
    algorithm: str = "ed25519"

    def to_dict(self) -> dict:
        return {
            "algorithm": self.algorithm,
            "payload_cbor_b64": base64.b64encode(self.payload_cbor).decode("ascii"),
            "signature_b64": base64.b64encode(self.signature).decode("ascii"),
            "public_key_b64": self.public_key_b64,
        }


class Ed25519Signer:
    """Wraps an Ed25519 private key for signing receipts."""

    def __init__(self, private_key: Ed25519PrivateKey):
        self._sk = private_key
        self._pk: Ed25519PublicKey = private_key.public_key()

    @classmethod
    def generate(cls) -> "Ed25519Signer":
        return cls(Ed25519PrivateKey.generate())

    def sign(self, message: bytes) -> bytes:
        return self._sk.sign(message)

    @property
    def public_key_bytes(self) -> bytes:
        return self._pk.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

    @property
    def public_key_b64(self) -> str:
        return base64.b64encode(self.public_key_bytes).decode("ascii")

    def verify(self, signature: bytes, message: bytes) -> bool:
        try:
            self._pk.verify(signature, message)
            return True
        except Exception:
            return False


def load_signer_from_pem(path: Union[str, Path, "os.PathLike[str]"],
                          password: bytes | None = None) -> Ed25519Signer:
    """Load an Ed25519 private key from a PEM file."""
    data = Path(path).read_bytes()
    key = serialization.load_pem_private_key(data, password=password)
    if not isinstance(key, Ed25519PrivateKey):
        raise ValueError("PEM file does not contain an Ed25519 private key.")
    return Ed25519Signer(key)


def verify_signature(public_key_b64: str, signature: bytes, message: bytes) -> bool:
    """Local verification helper — C4 (local verification only)."""
    raw = base64.b64decode(public_key_b64)
    pk = Ed25519PublicKey.from_public_bytes(raw)
    try:
        pk.verify(signature, message)
        return True
    except Exception:
        return False
