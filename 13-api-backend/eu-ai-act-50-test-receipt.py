#!/usr/bin/env python3
"""
eu-ai-act-50-test-receipt.py
────────────────────────────
End-to-end EU AI Act Article 50 receipt issuance for the LedgerProof EU API
smoke test (Test 5 of EU-SMOKE-TEST-PLAN.md).

Steps performed:
  1. Load or generate an Ed25519 keypair
  2. Register the verifying key at POST /v1/keys
  3. Detect the current chain tip (sequence + prev_hash)
  4. Build the eu_ai_act_50 content payload
  5. Construct entry_json_canonical (sorted-key JSON, matching Rust serde_json output)
  6. Compute entry_hash = SHA-256(entry_json_canonical)
  7. Sign the 32-byte entry_hash with Ed25519
  8. Submit to POST /v1/publish
  9. Print the receipt response

Usage:
  python3 eu-ai-act-50-test-receipt.py \\
    --api-base https://ledgerproof-api-eu.fly.dev \\
    --api-key lp_... \\
    --publisher-id eu-smoke-test-001 \\
    --key-id smoke-key-001

  # Reuse an existing keypair (from a previous run):
  python3 eu-ai-act-50-test-receipt.py \\
    --api-base https://ledgerproof-api-eu.fly.dev \\
    --api-key lp_... \\
    --publisher-id eu-smoke-test-001 \\
    --key-id smoke-key-001 \\
    --signing-key-hex <64-char hex from previous run>

Dependencies:
  pip3 install requests cryptography
"""

import argparse
import base64
import hashlib
import json
import sys
from datetime import datetime, timezone

# ── Dependency checks ─────────────────────────────────────────────────────────
try:
    import requests
except ImportError:
    print("ERROR: 'requests' not installed. Run: pip3 install requests", file=sys.stderr)
    sys.exit(1)

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
except ImportError:
    print("ERROR: 'cryptography' not installed. Run: pip3 install cryptography", file=sys.stderr)
    sys.exit(1)


# ── Helpers ───────────────────────────────────────────────────────────────────

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(obj) -> str:
    """
    Produce compact, deterministically sorted JSON.

    This matches Rust's serde_json::to_string() behaviour when the Value was
    parsed from a sort_keys-serialised string: serde_json uses IndexMap (insertion
    order), so as long as we sort on the way in, both sides produce the same bytes.
    """
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


def step(n: int, msg: str):
    print(f"\n[Step {n}] {msg}")


def ok(msg: str):
    print(f"  ✓ {msg}")


def fail(msg: str):
    print(f"  ✗ {msg}", file=sys.stderr)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="LedgerProof EU AI Act Article 50 end-to-end smoke test"
    )
    parser.add_argument(
        "--api-base", default="https://ledgerproof-api-eu.fly.dev",
        help="Base URL of the EU operator (default: fly.dev hostname)"
    )
    parser.add_argument("--api-key", required=True, help="Raw publisher API key (lp_...)")
    parser.add_argument("--publisher-id", required=True, help="Publisher ID provisioned in Test 4")
    parser.add_argument("--key-id", default="smoke-key-001", help="Key ID to register/reuse")
    parser.add_argument(
        "--signing-key-hex",
        help="Hex-encoded 32-byte Ed25519 raw private key. Omit to generate a fresh keypair."
    )
    parser.add_argument(
        "--sequence", type=int, default=None,
        help="Override the expected next sequence (auto-detected by default)"
    )
    parser.add_argument(
        "--prev-hash", default=None,
        help="Override prev_hash (auto-detected by default; 64 zeros for genesis)"
    )
    args = parser.parse_args()

    base = args.api_base.rstrip("/")
    auth_headers = {
        "X-Api-Key": args.api_key,
        "X-Publisher-Id": args.publisher_id,
    }

    # ── Step 1: Keypair ───────────────────────────────────────────────────────
    step(1, "Loading Ed25519 keypair")
    if args.signing_key_hex:
        if len(args.signing_key_hex) != 64:
            fail("--signing-key-hex must be exactly 64 hex characters (32 bytes)")
            sys.exit(1)
        sk_bytes = bytes.fromhex(args.signing_key_hex)
        private_key = Ed25519PrivateKey.from_private_bytes(sk_bytes)
        ok(f"Using existing key: {args.signing_key_hex[:16]}…")
    else:
        private_key = Ed25519PrivateKey.generate()
        sk_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )
        print(f"  Generated new Ed25519 keypair.")
        print(f"  ┌─ Save this to reuse the key on subsequent runs:")
        print(f"  │  SIGNING_KEY_HEX={sk_bytes.hex()}")
        print(f"  └─────────────────────────────────────────────────")

    public_key = private_key.public_key()
    vk_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    vk_b64 = base64.b64encode(vk_bytes).decode()
    ok(f"Verifying key (b64): {vk_b64[:20]}…")

    # ── Step 2: Register verifying key ────────────────────────────────────────
    step(2, f"Registering key '{args.key_id}' at POST /v1/keys")
    reg_resp = requests.post(
        f"{base}/v1/keys",
        headers={**auth_headers, "Content-Type": "application/json"},
        json={"key_id": args.key_id, "verifying_key_b64": vk_b64},
        timeout=15,
    )
    if reg_resp.status_code == 201:
        eff = reg_resp.json().get("effective_from_sequence", "?")
        ok(f"Registered — effective_from_sequence={eff}")
    else:
        fail(f"Key registration returned HTTP {reg_resp.status_code}: {reg_resp.text}")
        sys.exit(1)

    # ── Step 3: Detect chain tip ───────────────────────────────────────────────
    step(3, "Detecting chain tip (sequence + prev_hash)")
    if args.sequence is not None and args.prev_hash is not None:
        sequence = args.sequence
        prev_hash = args.prev_hash
        ok(f"Using supplied: sequence={sequence}, prev_hash={prev_hash[:16]}…")
    else:
        # Walk forward from sequence 0 to find the tip.
        # Stops at the first 404 (that sequence doesn't exist yet → that's our next slot).
        probe = 0
        while True:
            r = requests.get(f"{base}/v1/entries/{probe}", timeout=10)
            if r.status_code == 404:
                sequence = probe
                prev_hash = ("0" * 64) if probe == 0 else (
                    requests.get(f"{base}/v1/entries/{probe - 1}", timeout=10)
                    .json()["entry_hash"]
                )
                break
            elif r.status_code == 200:
                probe += 1
                if probe > 10_000:
                    fail("Chain has >10 000 entries — pass --sequence and --prev-hash explicitly")
                    sys.exit(1)
            else:
                fail(f"Unexpected HTTP {r.status_code} probing sequence {probe}: {r.text}")
                sys.exit(1)
        ok(f"Next sequence={sequence}, prev_hash={prev_hash[:16]}…")

    # ── Step 4: Build EU AI Act Article 50 content ────────────────────────────
    step(4, "Building eu_ai_act_50 content payload")

    # Required fields: ai_system_id, deployer_id, content_category
    # Optional: ai_system_version, deployer_name, deployer_country
    # Omit: artifact_hash, artifact_content_type, artifact_bytes (not needed for smoke test)
    # Required fields per AiArticle50Content struct (quantum-edge-2/src/schemas.rs):
    #   ai_system_id, deployer_id, deployer_name, deployer_country,
    #   content_category, artifact_hash, artifact_content_type, artifact_bytes
    # Optional (skip_serializing_if = None): ai_system_version, supervisory_authority
    # LPR v1.1 additions (all optional, server-side defaults apply if omitted):
    #   generation_type, source_content_hash, perceptual_hash, transparency_marker,
    #   is_public_interest, enforcement_date, profile_version
    SMOKE_TEXT = b"LedgerProof EU smoke test artifact"
    artifact_hash_val = sha256_hex(SMOKE_TEXT)

    content = {
        # v1.0 base fields
        "ai_system_id":           "test-ai-system-ledgerproof-smoke-001",
        "ai_system_version":      "1.0.0",
        "artifact_bytes":         len(SMOKE_TEXT),
        "artifact_content_type":  "text/plain",
        "artifact_hash":          artifact_hash_val,
        "content_category":       "SYNTHETIC_TEXT",
        "deployer_country":       "US",
        "deployer_id":            "LedgerProof-Foundation-EU-Pilot",
        "deployer_name":          "LedgerProof Foundation",
        # v1.1 additions — exercise the new fields end-to-end
        "generation_type":        "FULLY_GENERATED",
        "transparency_marker":    "AI-GENERATED: LedgerProof smoke-test artifact (LPR v1.1)",
        "is_public_interest":     False,
        "enforcement_date":       "2026-08-02",
        "profile_version":        "EU-AI-ACT-50-v1.1",
    }

    # content_hash = SHA-256 of the canonical (sorted-key) JSON of the content object.
    # The server re-serialises the 'content' field from the parsed canonical entry JSON
    # and hashes that — because we sort keys identically on both sides, the hashes match.
    content_canonical = canonical_json(content)
    content_hash = sha256_hex(content_canonical.encode("utf-8"))
    ok(f"content_type=ai/article-50/v1")
    ok(f"content_hash={content_hash[:16]}…")

    # ── Step 5: Build entry_json_canonical ────────────────────────────────────
    step(5, "Constructing entry_json_canonical")

    # ISO-8601 timestamp with millisecond precision and Z suffix.
    # Used both in the canonical record and in the POST body.
    now = datetime.now(timezone.utc)
    entry_timestamp = now.strftime("%Y-%m-%dT%H:%M:%S") + f".{now.microsecond // 1000:03d}Z"

    # All fields that uniquely identify this entry.  Keys are sorted so that
    # serde_json's re-serialisation of the parsed Value produces the same bytes.
    entry_obj = {
        "content":           content,          # embedded as object, sorted recursively
        "content_hash":      content_hash,
        "content_type":      "ai/article-50/v1",
        "entry_timestamp":   entry_timestamp,
        "key_id":            args.key_id,
        "prev_hash":         prev_hash,
        "protocol_version":  "ledgerproof/1.0",
        "publisher_id":      args.publisher_id,
        "sequence":          sequence,
    }

    entry_json_canonical = canonical_json(entry_obj)
    entry_hash = sha256_hex(entry_json_canonical.encode("utf-8"))
    ok(f"entry_json_canonical built ({len(entry_json_canonical)} bytes)")
    ok(f"entry_hash={entry_hash[:16]}…")

    # ── Step 6: Sign entry_hash bytes ─────────────────────────────────────────
    step(6, "Signing entry_hash with Ed25519")

    # The server verifies: verifying_key.verify(&entry_hash_bytes, &signature)
    # where entry_hash_bytes = hex::decode(&req.entry_hash)
    # So we sign the raw 32 bytes of the hash, not the hex string.
    entry_hash_bytes = bytes.fromhex(entry_hash)
    sig_bytes = private_key.sign(entry_hash_bytes)
    signature_hex = sig_bytes.hex()
    ok(f"signature={signature_hex[:16]}… ({len(sig_bytes)} bytes)")

    # ── Step 7: POST /v1/publish ───────────────────────────────────────────────
    step(7, f"Submitting to {base}/v1/publish")

    publish_body = {
        "publisher_id":        args.publisher_id,
        "key_id":              args.key_id,
        "prev_hash":           prev_hash,
        "entry_hash":          entry_hash,
        "signature":           signature_hex,
        "protocol_version":    "ledgerproof/1.0",
        "content_type":        "ai/article-50/v1",
        "content_hash":        content_hash,
        "content":             content,
        "entry_json_canonical": entry_json_canonical,
        "entry_timestamp":     entry_timestamp,
    }

    pub_resp = requests.post(
        f"{base}/v1/publish",
        headers={**auth_headers, "Content-Type": "application/json"},
        json=publish_body,
        timeout=15,
    )

    # ── Result ────────────────────────────────────────────────────────────────
    print()
    if pub_resp.status_code == 201:
        result = pub_resp.json()
        print("╔══════════════════════════════════════╗")
        print("║  ✅  Receipt issued successfully      ║")
        print("╚══════════════════════════════════════╝")
        print(json.dumps(result, indent=2))
        seq_out = result.get('sequence')
        print(f"\nVerify (Test 6):")
        print(f"  curl -s {base}/v1/entries/{seq_out} | python3 -m json.tool")
        print(f"\nErase (Test 7):")
        print(f"  curl -i -X DELETE {base}/v1/entries/{seq_out} \\")
        print(f"    -H 'X-Api-Key: {args.api_key}' \\")
        print(f"    -H 'X-Publisher-Id: {args.publisher_id}'")
    elif pub_resp.status_code == 409:
        fail(f"Sequence conflict (409): {pub_resp.text}")
        print("  Retry with the correct --sequence and --prev-hash from:")
        print(f"  curl -s {base}/v1/entries/<last_seq> | python3 -m json.tool")
        sys.exit(1)
    else:
        fail(f"Publish failed HTTP {pub_resp.status_code}")
        try:
            print(json.dumps(pub_resp.json(), indent=2))
        except Exception:
            print(pub_resp.text)
        sys.exit(1)


if __name__ == "__main__":
    main()
