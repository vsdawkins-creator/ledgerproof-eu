---
title: Verify someone else's receipt
description: How regulators, journalists, courts, and curious users can verify any LPR receipt.
---

LedgerProof receipts are designed to be verified by **anyone**, without an
account, without authentication, and without contacting the issuer.

## Method 1 — Public web tool

Visit [search.ledgerproofhq.io](https://search.ledgerproofhq.io). You can:

- Verify by sequence number (e.g., `42`)
- Look up by content hash (SHA-256 of the artifact)
- Hash a file locally in your browser and look up its receipt

The file never leaves your browser.

## Method 2 — Browser extension

Install the [LedgerProof Verifier](https://chrome.google.com/webstore/...)
extension for Chrome, Firefox, or Safari. It automatically decorates any
page with `data-lpr-receipt` markers with a verification badge.

Permissions:
- Only `activeTab` — does NOT have access to all pages
- Network: only `api-eu.ledgerproofhq.io`
- No telemetry, no analytics, no history

## Method 3 — Direct HTTPS

```
curl https://api-eu.ledgerproofhq.io/v1/verify/42
```

Returns the full receipt as JSON. No auth headers required.

For high-volume verification, use:

```
curl https://api-eu.ledgerproofhq.io/v1/receipts/by-content-hash/{sha256}
```

Returns all receipts whose content hash matches.

## Method 4 — Bulk verification

For media monitoring services, journalist consortia, market surveillance
authorities: contact [veronica@ledgerproofhq.io](mailto:veronica@ledgerproofhq.io)
for a dedicated bulk-verification API key with higher rate limits.

## What "verified" means

A verified receipt means:

1. The receipt exists on the LedgerProof EU operator's append-only chain.
2. The Ed25519 signature over the canonical entry was issued by the
   registered publisher key.
3. (Once anchored) The receipt's hash is committed in a Bitcoin OP_RETURN
   transaction with at least 6 confirmations.

A verified receipt does **not** assert that the AI-generated content was
accurate, lawful, or not defamatory — only that the named deployer issued
it at the specified time.
