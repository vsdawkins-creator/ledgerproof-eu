"""
LedgerProof Foundation — governance event anchor tool.

Eats our own cooking: every Foundation governance event becomes a signed,
canonically-encoded receipt anchored to Bitcoin via OpenTimestamps.

INTERIM KEY DISCLOSURE: Until the Foundation root-key ceremony (Aug 15, 2026),
this tool signs with an interim Ed25519 key stored at ~/.ledgerproof-secrets/.
The interim key's public half is published in every emitted receipt and in
ops-state.json. Post-ceremony, the interim key is rotated to a 2-of-3 multisig
via a documented key-transition receipt that itself is signed by the interim key
(establishing an unbroken authority chain).

Usage:
    python tools/foundation_anchor.py anchor <file_to_anchor> \
        --event-type consultation_submission \
        --metadata "key=value,key2=value2" \
        --output-dir 17-futurium/anchored-receipts/<event-name>/
"""
import argparse
import base64
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization

KEY_PATH = Path.home() / ".ledgerproof-secrets" / "foundation-interim-signing-key.pem"
KEY_PATH.parent.mkdir(mode=0o700, exist_ok=True)


def load_or_create_key() -> Ed25519PrivateKey:
    """Load the interim Foundation signing key. Create if it doesn't exist."""
    if KEY_PATH.exists():
        with open(KEY_PATH, "rb") as f:
            return serialization.load_pem_private_key(f.read(), password=None)

    print(f"INTERIM KEY GENERATION: creating new Ed25519 key at {KEY_PATH}", file=sys.stderr)
    key = Ed25519PrivateKey.generate()
    pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    with open(KEY_PATH, "wb") as f:
        f.write(pem)
    KEY_PATH.chmod(0o600)
    return key


def public_key_b64(key: Ed25519PrivateKey) -> str:
    """Return Base64-encoded raw Ed25519 public key (32 bytes)."""
    raw = key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return base64.b64encode(raw).decode("ascii")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(obj) -> bytes:
    """Deterministic JSON canonicalization: sorted keys, no whitespace."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def build_receipt(
    anchored_file_path: Path,
    event_type: str,
    metadata: dict,
    signing_key: Ed25519PrivateKey,
) -> dict:
    """Build a foundation_governance_event/v1 receipt."""
    file_bytes = anchored_file_path.read_bytes()
    file_hash = sha256_hex(file_bytes)
    file_size = len(file_bytes)
    iso_now = datetime.now(timezone.utc).isoformat()

    # Receipt body (will be signed)
    body = {
        "schema": "foundation_governance_event/v1",
        "schema_url": "https://spec.ledgerproofhq.io/schemas/foundation_governance_event/v1.json",
        "foundation": "LedgerProof Foundation",
        "foundation_status": "in_formation_us_501c3_delaware_plus_dutch_stichting_amsterdam",
        "event_type": event_type,
        "event_timestamp_iso": iso_now,
        "anchored_file": {
            "filename": anchored_file_path.name,
            "sha256": file_hash,
            "size_bytes": file_size,
        },
        "metadata": metadata,
        "signing_key": {
            "algorithm": "Ed25519",
            "public_key_b64": public_key_b64(signing_key),
            "key_authority_chain_position": "interim_pre_root_ceremony",
            "key_ceremony_target_date": "2026-08-15",
            "key_authority_disclosure": (
                "This receipt is signed by the Foundation's interim Ed25519 signing key. "
                "The Foundation root-key ceremony (Aug 15, 2026) will rotate to a 2-of-3 "
                "multisig via a documented key-transition receipt signed by this interim key, "
                "establishing an unbroken authority chain."
            ),
        },
        "protocol_version": "LPR-1.1.1rc0",
        "anchor_method": "opentimestamps_bitcoin_mainnet",
        "anchor_status": "pending_aggregator_confirmation",
    }

    # Canonical encoding + signature
    canonical_body_bytes = canonical_json(body)
    canonical_body_hash = sha256_hex(canonical_body_bytes)
    signature = signing_key.sign(canonical_body_bytes)
    signature_b64 = base64.b64encode(signature).decode("ascii")

    return {
        "body": body,
        "canonical_body_sha256": canonical_body_hash,
        "signature_algorithm": "Ed25519-over-canonical-JSON-utf8",
        "signature_b64": signature_b64,
    }


def opentimestamps_stamp(file_path: Path) -> tuple[bool, str]:
    """Anchor the file via OpenTimestamps. Returns (success, ots_proof_path_or_msg)."""
    ots_file = Path(str(file_path) + ".ots")
    try:
        result = subprocess.run(
            ["ots", "stamp", str(file_path)],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            return False, f"OTS stamp failed: stderr={result.stderr}, stdout={result.stdout}"
        if ots_file.exists():
            return True, str(ots_file)
        return False, f"OTS stamp returned success but no .ots file at {ots_file}"
    except FileNotFoundError:
        return False, "ots client not found in PATH. Install with: pip install opentimestamps-client"
    except subprocess.TimeoutExpired:
        return False, "OTS stamp timed out after 60s"


def main():
    p = argparse.ArgumentParser(description="Anchor a Foundation governance event")
    p.add_argument("action", choices=["anchor"])
    p.add_argument("file", help="File to anchor (PDF, image, JSON, etc.)")
    p.add_argument("--event-type", required=True,
                   help="Event type slug (e.g., consultation_submission, board_minutes)")
    p.add_argument("--metadata", default="",
                   help="Comma-separated key=value pairs")
    p.add_argument("--output-dir", required=True,
                   help="Directory to save the anchored receipt bundle")
    args = p.parse_args()

    file_path = Path(args.file).resolve()
    if not file_path.exists():
        print(f"ERROR: file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    metadata = {}
    if args.metadata:
        for pair in args.metadata.split(","):
            if "=" in pair:
                k, v = pair.split("=", 1)
                metadata[k.strip()] = v.strip()

    key = load_or_create_key()
    print(f"[1/4] Foundation interim key loaded. Public key (Base64): {public_key_b64(key)}")

    receipt = build_receipt(file_path, args.event_type, metadata, key)
    print(f"[2/4] Receipt built. Canonical body SHA-256: {receipt['canonical_body_sha256']}")

    # Write receipt JSON
    receipt_path = output_dir / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True))
    print(f"[3/4] Receipt written: {receipt_path}")

    # Copy the anchored file to the output dir so the bundle is self-contained
    import shutil
    anchored_copy = output_dir / file_path.name
    if not anchored_copy.exists() or anchored_copy.resolve() != file_path:
        shutil.copy2(file_path, anchored_copy)
    print(f"        Anchored file copied: {anchored_copy}")

    # Anchor via OpenTimestamps
    print(f"[4/4] Submitting to OpenTimestamps (Bitcoin aggregator)...")
    success, msg = opentimestamps_stamp(receipt_path)
    if success:
        print(f"        OTS proof: {msg}")
        print(f"        Status: pending Bitcoin block confirmation (~1-6 hours)")
        print(f"        To upgrade later: ots upgrade {msg}")
        print(f"        To verify later: ots verify {receipt_path}")

        # Write a README to the bundle
        readme_path = output_dir / "README.md"
        readme_path.write_text(f"""# Foundation Governance Event — {args.event_type}

**Event timestamp**: {receipt['body']['event_timestamp_iso']}
**Anchored file**: `{file_path.name}` (SHA-256: `{receipt['body']['anchored_file']['sha256']}`)
**Receipt**: `receipt.json` (canonical SHA-256: `{receipt['canonical_body_sha256']}`)
**OpenTimestamps proof**: `receipt.json.ots`

## Verification

To verify the anchor (after Bitcoin confirmation, typically within 1-6 hours):

```bash
ots upgrade receipt.json.ots
ots verify receipt.json
```

To verify the signature:

```python
import json, base64, hashlib
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

receipt = json.load(open("receipt.json"))
canonical = json.dumps(receipt["body"], sort_keys=True, separators=(",",":"), ensure_ascii=False).encode("utf-8")

pub_b64 = receipt["body"]["signing_key"]["public_key_b64"]
pub_raw = base64.b64decode(pub_b64)
pub_key = Ed25519PublicKey.from_public_bytes(pub_raw)

sig = base64.b64decode(receipt["signature_b64"])
pub_key.verify(sig, canonical)
print("Signature verified.")
```

## Interim key disclosure

This receipt is signed by the Foundation's interim Ed25519 signing key (created
{datetime.now(timezone.utc).strftime("%Y-%m-%d")} when no Foundation governance
events had yet been anchored). The Foundation root-key ceremony scheduled for
August 15, 2026 will rotate to a 2-of-3 multisig. The rotation will be itself
recorded as a Foundation governance event, signed by this interim key,
establishing an unbroken key authority chain.

## Self-attesting metadata

""" + "\n".join(f"- **{k}**: {v}" for k, v in metadata.items()))
        print(f"        README written: {readme_path}")
        print(f"\n✓ Anchored governance event bundle complete: {output_dir}")
    else:
        print(f"        OTS anchor FAILED: {msg}", file=sys.stderr)
        print(f"        Receipt is signed but NOT anchored. Re-run anchor step when ots is available.")
        sys.exit(2)


if __name__ == "__main__":
    main()
