---
title: What is an LPR receipt?
description: The anatomy of a LedgerProof Receipt — every field, what it means, why it's there.
---

A LedgerProof Receipt (LPR) is a machine-readable cryptographic record that
attests to the provenance of a piece of content — typically AI-generated text,
image, audio, or video — for the purpose of EU AI Act Article 50 compliance.

## Anatomy

A v1.1 receipt has three layers:

1. **Envelope** — chain identity (sequence, prev_hash, entry_hash, signature)
2. **Content** — the Article 50 metadata (deployer, AI system, content hash)
3. **Anchor** — Bitcoin commitment (txid, block height, Merkle path)

### Example

```json
{
  "sequence": 42,
  "publisher_id": "LEI:5493001KJTIIGC8Y1R12",
  "key_id": "production-key-001",
  "prev_hash": "a1b2c3d4...",
  "entry_hash": "e5f6a7b8...",
  "signature": "9c0d1e2f...",
  "protocol_version": "ledgerproof/1.0",
  "content_type": "ai/article-50/v1",
  "content_hash": "0123abcd...",
  "content": {
    "ai_system_id": "openai/gpt-4o/2024-11-20",
    "deployer_id": "LEI:5493001KJTIIGC8Y1R12",
    "deployer_name": "Acme Insurance AG",
    "deployer_country": "DE",
    "content_category": "SYNTHETIC_TEXT",
    "artifact_hash": "f4e3d2c1...",
    "artifact_content_type": "text/plain",
    "artifact_bytes": 1024,
    "generation_type": "FULLY_GENERATED",
    "transparency_marker": "LPR-EU-AI-ACT-50",
    "is_public_interest": false,
    "enforcement_date": "2026-08-02",
    "profile_version": "EU-AI-ACT-50-v1.1"
  },
  "entry_timestamp": "2026-09-15T12:34:56.789Z",
  "anchor": {
    "status": "CONFIRMED",
    "btc_txid": "5db5c68e...",
    "btc_block_height": 900123
  }
}
```

### Key fields explained

| Field | Purpose |
|---|---|
| `sequence` | Position in the publisher's chain. Strictly monotonic. |
| `entry_hash` | SHA-256 of the canonical entry. The receipt's immutable identity. |
| `signature` | Ed25519 over `entry_hash`. Proves the publisher key signed this. |
| `content_hash` | SHA-256 of canonical content JSON. Lets the server verify the content matches what was signed. |
| `artifact_hash` | SHA-256 of the actual content (text/image/audio/video). The content stays local; only this hash is anchored. |
| `transparency_marker` | The human-readable disclosure string Article 50 requires. |
| `is_public_interest` | Whether this content triggers Article 50(4). |
| `deployer_id` | Legal entity identifier (LEI/EUID/VAT/DID). Never an email. |

## What's NOT in a receipt

- The actual content (text, image, audio, video) — **stays on your servers**
- Personal data of the deployer (no names, emails, addresses)
- Personal data of the reviewer (only role identifiers like "senior-editor")
- The prompt that produced the content (deployer's choice whether to record
  a `prompt_hash` separately)

## What "verified" guarantees

A verified LPR receipt proves:

1. The named `deployer_id` issued this receipt at the named `entry_timestamp`.
2. The receipt has not been altered since.
3. The receipt's hash is committed to Bitcoin (once anchored).

It does NOT prove:

- That the content was accurate, lawful, or non-defamatory
- That the AI system worked correctly
- That the human reviewer (in a 50(4) chain) actually reviewed it

LPR is the **cryptographic provenance layer**. Other layers — fact-checking,
watermarking, content classification — sit alongside it.

## See also

- [Why Bitcoin anchoring?](/explain/why-bitcoin/)
- [LPR v1.1 specification](/reference/lpr-spec/)
- [Article 50 overview](/explain/article-50/)
