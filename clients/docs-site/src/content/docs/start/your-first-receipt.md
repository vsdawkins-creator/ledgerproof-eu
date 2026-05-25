---
title: Your first LPR receipt
description: Issue a Bitcoin-anchored EU AI Act Article 50 receipt in five minutes.
---

By the end of this tutorial you will have issued a real LedgerProof receipt
against the production EU operator and verified it via the public endpoint.

## What you need

- Python 3.9+ (or Node 18+ — both SDKs documented)
- An LedgerProof publisher API key (`lp_...`). Get one by emailing
  [veronica@ledgerproofhq.io](mailto:veronica@ledgerproofhq.io) or
  provisioning via your operator's admin endpoint.
- 5 minutes.

## Install the SDK

```bash
pip install ledgerproof
```

## Set credentials

Either via environment variables:

```bash
export LEDGERPROOF_API_KEY=lp_xxxx
export LEDGERPROOF_PUBLISHER_ID="LEI:5493001KJTIIGC8Y1R12"
```

Or pass them inline (see below).

## Issue a receipt

```python
from ledgerproof import LedgerProof

lp = LedgerProof(
    publisher_id="LEI:5493001KJTIIGC8Y1R12",
    deployer_country="DE",
)

receipt = lp.publish_ai_article_50(
    artifact="The generated article text...",
    artifact_content_type="text/plain",
    ai_system_id="openai/gpt-4o/2024-11-20",
    deployer_name="Acme Insurance AG",
    content_category="SYNTHETIC_TEXT",
)

print(receipt.sequence)        # → e.g., 42
print(receipt.entry_hash)      # → 64-char SHA-256
print(receipt.verify_url)      # → https://api-eu.ledgerproofhq.io/v1/verify/42
```

The artifact (the actual text) is hashed locally. **It never leaves your
machine.** Only the SHA-256 is transmitted to LedgerProof.

## Verify the receipt

```python
entry = lp.verify(receipt.sequence)
print(entry.entry_hash == receipt.entry_hash)  # → True
print(entry.signature)                          # → 128-char hex Ed25519 sig
```

Or visit the verify URL in your browser — no authentication required.

## What just happened

1. The SDK generated an Ed25519 keypair and saved it to
   `~/.config/ledgerproof/signing_key.bin` (mode 0600).
2. It registered the public key with the EU operator.
3. It hashed your artifact, built the canonical entry, signed it.
4. It POSTed to `/v1/publish`.
5. The operator validated the schema, persisted the entry, and returned the
   receipt.
6. The receipt's `entry_hash` will be batched into a Merkle tree and anchored
   to Bitcoin mainnet on the next anchor cycle (daily).

## Next steps

- [Add LPR to your LangChain pipeline →](/how-to/langchain/)
- [Add LPR to a Next.js app →](/how-to/nextjs/)
- [Read the LPR v1.1 specification →](/reference/lpr-spec/)
