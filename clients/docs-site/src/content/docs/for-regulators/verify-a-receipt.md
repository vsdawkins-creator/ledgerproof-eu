---
title: Verify a LedgerProof receipt — for regulators
description: Step-by-step verification procedure for market surveillance authorities, courts, and competent regulators.
---

This page is intended for market surveillance authorities, competent regulators
under the EU AI Act, and courts of EU Member States. It describes the formal
verification procedure for an LPR receipt presented as evidence of Article 50
compliance.

## Standing public infrastructure

LedgerProof Foundation operates a public verifier at:

**Production EU endpoint:** `https://api-eu.ledgerproofhq.io`

The endpoint is:

- Frankfurt-hosted (EU data residency)
- Free to query, no authentication required
- Documented at `https://docs.ledgerproofhq.io/reference/api/`
- Available in JSON and CBOR formats

## Verification procedure

### Step 1 — Identify the receipt

A receipt can be referenced by:

- **Sequence number** (e.g., `42`) — the position in the operator's chain
- **Entry hash** (64-char SHA-256) — the receipt's immutable identifier
- **Content hash** (64-char SHA-256 of the artifact) — finds the receipt
  given the suspect content itself

### Step 2 — Fetch the receipt

```bash
# By sequence
curl https://api-eu.ledgerproofhq.io/v1/verify/42

# By content hash
curl https://api-eu.ledgerproofhq.io/v1/receipts/by-content-hash/{sha256}
```

### Step 3 — Validate the response

A valid receipt response includes:

| Field | Validation |
|---|---|
| `sequence` | Integer ≥ 0 |
| `entry_hash` | 64-char lowercase hex |
| `signature` | 128-char hex (Ed25519, 64 bytes) |
| `content_type` | `ai/article-50/v1`, `ai/human-review/v1`, or `ai/chatbot-session/v1` |
| `entry_timestamp` | ISO 8601 datetime |
| `content.deployer_id` | Legal entity identifier (LEI/EUID/VAT/DID) |
| `content.deployer_country` | ISO 3166-1 alpha-2 |

### Step 4 — Confirm the Bitcoin anchor

For receipts with `anchor_status = "CONFIRMED"`:

1. Fetch the `btc_txid` from the receipt response.
2. Query any Bitcoin block explorer (mempool.space, blockstream.info,
   or run your own node):
   ```
   https://mempool.space/api/tx/{btc_txid}
   ```
3. Confirm the OP_RETURN data field contains `LPR1` + 32-byte Merkle root.
4. Confirm the receipt's `entry_hash` is included in the Merkle tree via
   the `merkle_path` field of the response.

### Step 5 — Validate the signature

The receipt is signed by the deployer's Ed25519 key. To verify:

1. Fetch the public key from `https://api-eu.ledgerproofhq.io/v1/keys?publisher_id={pid}`.
2. The signature in the receipt is over the raw 32-byte SHA-256 of
   `entry_json_canonical`.
3. Use any Ed25519 verifier to confirm.

The Python SDK does this automatically:

```python
from ledgerproof import LedgerProof
lp = LedgerProof(publisher_id="DID:verifier-only", deployer_country="XX",
                 api_key="noop")
entry = lp.verify(sequence=42)
# Signature check is implicit; if it fails the server returns 422.
```

## Evidence bundle (for proceedings)

For evidentiary submission, LedgerProof provides a one-call evidence bundle
export endpoint that returns:

- The receipt + full canonical entry JSON
- The Ed25519 public key + key registration history for the publisher
- The Bitcoin anchor proof (txid, block hash, Merkle path)
- A timestamped attestation signed by the LedgerProof operator key
- A PDF rendering suitable for court filing

```
GET https://api-eu.ledgerproofhq.io/v1/evidence-bundle/{sequence}.pdf
```

## Contact

For coordinated verification at scale, formal evidence requests, or
enforcement collaboration:

- **Foundation contact:** veronica@ledgerproofhq.io
- **EU AI Office:** CNECT-AIOFFICE@ec.europa.eu (cc'd on LedgerProof Foundation correspondence)

## Multi-jurisdiction

For non-EU jurisdictions, LedgerProof receipts use the same protocol with
different content type profiles (e.g., `ai/uk-ai-bill/v1` for UK, planned
Q3 2026). The verification procedure is identical.
