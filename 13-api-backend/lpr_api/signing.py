"""
LPR API — Ed25519 signing key management.

The signing key is the identity of this calendar operator.
It MUST be:
  - Generated once with: python -m lpr_operator.keygen (or our keygen.py)
  - Stored at SIGNING_KEY_PATH (a Fly.io persistent volume mount)
  - NOT stored as an environment variable (it's ~32-byte raw private key —
    too sensitive even for secrets if the volume is more restricted)
  - Backed up offline before going to production

This module loads the key at startup and holds it in memory for the
lifetime of the process. If the key file is absent, startup fails
with a clear error message.
"""
from __future__ import annotations

import logging
import os
from typing import Optional

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

logger = logging.getLogger("lpr.signing")

_signer_key: Optional[Ed25519PrivateKey] = None
_signer_pubkey_hex: Optional[str] = None


def load_signing_key() -> None:
    """Load the Ed25519 signing key. Called once at startup.

    Source priority:
      1. OPERATOR_KEY_PEM env var (PEM contents directly — used in Fly.io deployments)
      2. SIGNING_KEY_PATH file (default /data/operator_key.pem — used for volume-based deployments)

    OPERATOR_KEY_PEM is preferred because it eliminates the need for a Fly volume
    and avoids any key material at rest on the container filesystem.
    """
    global _signer_key, _signer_pubkey_hex

    pem_data: bytes
    key_source: str

    pem_from_env = os.environ.get("OPERATOR_KEY_PEM")
    if pem_from_env:
        pem_data = pem_from_env.encode()
        key_source = "OPERATOR_KEY_PEM env var"
    else:
        key_path = os.environ.get("SIGNING_KEY_PATH", "/data/operator_key.pem")
        if not os.path.exists(key_path):
            raise FileNotFoundError(
                f"Signing key not found. Set either OPERATOR_KEY_PEM env var "
                f"(preferred — paste full PEM contents) or SIGNING_KEY_PATH to a "
                f"PEM file (default /data/operator_key.pem). "
                f"Generate a key with: python -m lpr_api.keygen --output <path>"
            )
        with open(key_path, "rb") as f:
            pem_data = f.read()
        key_source = f"file {key_path!r}"

    _signer_key = serialization.load_pem_private_key(pem_data, password=None)
    if not isinstance(_signer_key, Ed25519PrivateKey):
        raise TypeError(f"Expected Ed25519PrivateKey, got {type(_signer_key).__name__}")

    pubkey_bytes = _signer_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    _signer_pubkey_hex = pubkey_bytes.hex()
    logger.info(
        "Signing key loaded from %s. Public key: %s",
        key_source, _signer_pubkey_hex[:16] + "...",
    )


def get_signing_key() -> Ed25519PrivateKey:
    if _signer_key is None:
        raise RuntimeError("Signing key not loaded — call load_signing_key() at startup")
    return _signer_key


def get_signer_pubkey_hex() -> str:
    if _signer_pubkey_hex is None:
        raise RuntimeError("Signing key not loaded — call load_signing_key() at startup")
    return _signer_pubkey_hex
