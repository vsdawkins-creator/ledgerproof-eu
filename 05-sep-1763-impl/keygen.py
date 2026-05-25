"""
Generate an Ed25519 signing key for the LPR MCP interceptor.

Usage:
    python keygen.py --output ~/.lpr/interceptor.key

The key is written in PEM format with no passphrase. For production, use a
hardware-backed key store; this utility is for development and reference use.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def main() -> int:
    p = argparse.ArgumentParser(description="Generate an Ed25519 signing key for the LPR interceptor.")
    p.add_argument("--output", required=True, help="Path to write the PEM-encoded key.")
    args = p.parse_args()

    out = Path(args.output).expanduser()
    if out.exists():
        print(f"Refusing to overwrite {out}. Move or delete it first.", file=sys.stderr)
        return 1

    key = Ed25519PrivateKey.generate()
    pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(pem)
    out.chmod(0o600)

    pub = key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    import base64

    pub_b64 = base64.urlsafe_b64encode(pub).rstrip(b"=").decode("ascii")
    print(f"Wrote private key to {out} (mode 0600).")
    print(f"Public key (Ed25519, base64url): {pub_b64}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
