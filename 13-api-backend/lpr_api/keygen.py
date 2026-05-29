"""
LPR operator key generation utility.

Usage:
    python -m lpr_api.keygen --output /data/operator_key.pem

Generates an Ed25519 keypair. The private key is written in PEM format
to the specified path (mode 0600). The public key is printed to stdout
in hex for registration with the Foundation.

IMPORTANT:
  - Back up the private key offline before going to production.
  - If the key is lost, past anchors cannot be attributed to this operator.
  - The key path must match SIGNING_KEY_PATH in the environment.
"""
from __future__ import annotations

import argparse
import os
import stat
import sys

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def generate_and_save(output_path: str) -> str:
    """Generate a new Ed25519 keypair and save the private key PEM to output_path.

    Returns the hex-encoded public key.
    """
    if os.path.exists(output_path):
        print(f"ERROR: Key file already exists at {output_path!r}.", file=sys.stderr)
        print("If you want to regenerate, delete the existing file first.", file=sys.stderr)
        sys.exit(1)

    private_key = Ed25519PrivateKey.generate()
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # Write with restricted permissions (owner read/write only).
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(pem)
    os.chmod(output_path, stat.S_IRUSR | stat.S_IWUSR)  # 0600

    pubkey_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return pubkey_bytes.hex()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an LPR operator Ed25519 signing key")
    parser.add_argument("--output", required=True, help="Path to write the PEM private key")
    args = parser.parse_args()

    pubkey_hex = generate_and_save(args.output)

    print(f"Private key written to: {args.output}")
    print(f"Public key (hex):       {pubkey_hex}")
    print()
    print("Next steps:")
    print(f"  1. Set SIGNING_KEY_PATH={args.output} in your environment")
    print("  2. Back up the private key file to offline storage")
    print("  3. Register this public key with the LedgerProof Foundation:")
    print("     Email operators@ledgerproofhq.io with:")
    print(f"     - Public key: {pubkey_hex}")
    print("     - Your operator DID (e.g. did:web:calendar.yourdomain.com)")
    print("     - Your organization name and country")


if __name__ == "__main__":
    main()
