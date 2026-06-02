"""Ed25519 signing primitives for LedgerProof receipts.

Uses `cryptography` (PyCA) — battle-tested, FIPS-aligned.
"""

from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


@dataclass
class SigningKey:
    """Ed25519 signing key wrapper."""

    private_key: Ed25519PrivateKey
    key_id: str  # short fingerprint identifier (first 16 hex of pubkey)

    def sign(self, message: bytes) -> bytes:
        return self.private_key.sign(message)

    def public_key_bytes(self) -> bytes:
        return self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

    def public_key_b64(self) -> str:
        return base64.b64encode(self.public_key_bytes()).decode("ascii")


def _key_id_from_public(pub: Ed25519PublicKey) -> str:
    raw = pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return raw.hex()[:16]


def generate_signing_key() -> SigningKey:
    """Generate a fresh Ed25519 keypair."""
    sk = Ed25519PrivateKey.generate()
    return SigningKey(private_key=sk, key_id=_key_id_from_public(sk.public_key()))


def load_signing_key_from_path(path: str | Path) -> SigningKey:
    """Load an Ed25519 private key from a PEM file on disk."""
    p = Path(path)
    data = p.read_bytes()
    sk = serialization.load_pem_private_key(data, password=None)
    if not isinstance(sk, Ed25519PrivateKey):
        raise ValueError(f"Expected Ed25519 private key, got {type(sk).__name__}")
    return SigningKey(private_key=sk, key_id=_key_id_from_public(sk.public_key()))


def save_signing_key_to_path(key: SigningKey, path: str | Path) -> None:
    """Persist a signing key to a PEM file (mode 0600)."""
    p = Path(path)
    pem = key.private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    p.write_bytes(pem)
    try:
        os.chmod(p, 0o600)
    except OSError:
        # Windows or restricted FS — best-effort.
        pass


def load_or_generate_signing_key(path: str | Path | None = None) -> SigningKey:
    """Load from `path` if present, otherwise generate (and save if path given)."""
    if path is None:
        return generate_signing_key()
    p = Path(path)
    if p.exists():
        return load_signing_key_from_path(p)
    key = generate_signing_key()
    p.parent.mkdir(parents=True, exist_ok=True)
    save_signing_key_to_path(key, p)
    return key


def verify_signature(public_key_b64: str, message: bytes, signature: bytes) -> bool:
    """Verify an Ed25519 signature. C4: purely local, no network."""
    raw = base64.b64decode(public_key_b64)
    pub = Ed25519PublicKey.from_public_bytes(raw)
    try:
        pub.verify(signature, message)
        return True
    except Exception:
        return False
