# Audit-Ready Compliance Stamp PDF — Design Specification

**Document version:** v1.0 (May 2026)
**Purpose:** Define the exact layout, content, and generation pipeline for the one-page PDF that LedgerProof issues to a Customer at the end of every billing period (or on demand). The PDF is the artifact a General Counsel hands to a regulator. It must hold up under regulator scrutiny and inside-counsel sign-off in equal measure.

**Generation cadence:** Monthly by default. On-demand via `POST /v1/customers/{id}/compliance-stamp` (also exposed in the Customer dashboard).

---

## Design constraints

1. **One page, A4 portrait.** Two-page artifacts get truncated, lost, or misfiled in regulator workflows. One page only.
2. **Black ink on warm cream (#FAF7F0) background — printable on regulator-grade paper.** No design flourishes. No marketing color. The aesthetic is "official document," not "tech product."
3. **Every claim on the page is cryptographically verifiable.** No marketing claims. No "we believe." Only verifiable facts plus citations to the underlying receipt set.
4. **Verifiable in 10 seconds.** The QR code in the header resolves to the verifier portal. The regulator scans, the portal renders the PDF's claims live, and the chain anchors are re-verified against Bitcoin mainnet in real time.

---

## Layout (top to bottom)

### Header band (60mm tall)
- **Left:** LedgerProof Foundation wordmark (Iowan Old Style serif) + "Compliance Stamp" tagline (Inter)
- **Center:** Customer name + Stamp ID (UUIDv4)
- **Right:** QR code linking to `https://verify.ledgerproofhq.io/stamp/{stamp_id}`

### Issuance block (20mm tall)
- Issuer: LedgerProof Foundation (501(c)(3) in formation, EIN [TBD])
- Issued: [ISO 8601 timestamp UTC]
- Coverage period: [start] to [end] UTC
- Receipt count: [N]
- Bitcoin anchor block range: [block_height_low] to [block_height_high]
- Merkle root of stamp: [64-hex-char SHA-256]

### Compliance attestation table (110mm tall — primary content)

| Regulation | Sub-clause | Receipts covering | Verification |
|---|---|---|---|
| EU AI Act | Article 50(1) — chatbot disclosure | [N₁] of [N] | `verify.ledgerproofhq.io/stamp/{stamp_id}#art50-1` |
| EU AI Act | Article 50(2) — synthetic media labeling | [N₂] of [N] | `verify.ledgerproofhq.io/stamp/{stamp_id}#art50-2` |
| EU AI Act | Article 50(4) — AI-generated text labeling | [N₃] of [N] | `verify.ledgerproofhq.io/stamp/{stamp_id}#art50-4` |
| ISO/IEC 42001 | A.6.2.8 — event logs | [N₄] of [N] | `verify.ledgerproofhq.io/stamp/{stamp_id}#iso-a628` |
| ISO/IEC 42001 | A.8.3 — external reporting | [N₅] of [N] | `verify.ledgerproofhq.io/stamp/{stamp_id}#iso-a83` |
| NIST AI RMF | Govern 5 — accountability | [N₆] of [N] | `verify.ledgerproofhq.io/stamp/{stamp_id}#nist-gov5` |
| NIST AI RMF | Measure 2 — performance | [N₇] of [N] | `verify.ledgerproofhq.io/stamp/{stamp_id}#nist-meas2` |
| DORA | Article 28 — ICT third-party risk | [N₈] of [N] | `verify.ledgerproofhq.io/stamp/{stamp_id}#dora-28` |

### Exception block (15mm tall — only rendered if exceptions exist)

If any receipts during the coverage period failed to anchor within the SLO, this block lists them with:
- Receipt ID
- Failure reason
- Remediation timestamp
- Bitcoin block where the remediated anchor landed

**Critical design choice:** Exceptions are NEVER hidden. Regulators trust documents that show exceptions and explain them. Documents with no exceptions look like marketing material.

### Footer band (15mm tall)
- **Left:** Ed25519 signature over the canonical CBOR of the stamp content, encoded base64
- **Center:** Foundation Canonical Registry URL — `registry.ledgerproofhq.io/{stamp_id}` — for any third party to resolve disputes about the stamp's content
- **Right:** Page 1 of 1

---

## Verification flow (regulator's experience)

1. Regulator receives the PDF (typically from the Customer's General Counsel).
2. Regulator scans the QR code in the header.
3. Verifier portal loads with the Stamp ID pre-filled.
4. Portal makes three independent verifications in parallel:
   - Re-computes the Merkle root of all receipts in the coverage period from the public chain anchors
   - Verifies the Ed25519 signature in the footer against LedgerProof's published public key
   - Re-fetches each linked Bitcoin block and confirms the OP_RETURN entries match
5. Portal renders three green checkmarks (or red, with specific failure detail).
6. Total elapsed time: 8–12 seconds.

**No part of this flow requires trusting LedgerProof.** The regulator could re-implement the verifier from the public IETF spec and the public Bitcoin chain.

---

## Failure modes and how the PDF surfaces them

| Failure | How the PDF shows it |
|---|---|
| Some receipts failed to anchor within SLO | Exception block lists each one with remediation timestamp |
| Some receipts were soft-deleted under GDPR | Coverage counts in attestation table show "[Nᵢ] of [N] (M soft-deleted under Customer GDPR request)" |
| LedgerProof operator was offline for part of the period | Exception block explains the gap with start/end timestamps and Customer-side queue depth at recovery |
| Customer's signing key was rotated mid-period | Two signatures appear in footer, one for each key, with rotation timestamp |

Every failure mode is documented in the spec at `spec.ledgerproofhq.io/stamp-pdf`. Regulators can read it before they ever see a PDF.

---

## Generation pipeline (technical)

1. Customer requests a stamp for `[start, end]`.
2. Service queries the receipt store for all receipts where Customer is the issuer or deployer in the period.
3. Service computes the canonical Merkle tree of the receipt set (RFC 6962 with domain separation).
4. Service queries Bitcoin chain for all anchor entries whose Merkle roots are leaves of the stamp's Merkle tree, and verifies block confirmations ≥ 6.
5. Service computes coverage counts per regulation sub-clause.
6. Service writes the stamp as canonical CBOR, signs with the Foundation's Ed25519 stamp key.
7. Service renders the CBOR to a PDF using the layout above (LaTeX template at `pipeline.ledgerproofhq.io/stamp.tex`).
8. Service publishes the canonical CBOR to the Foundation Canonical Registry.
9. Customer receives the PDF + a permalink to the registry entry.

End-to-end generation time: <8 seconds for receipt counts up to 10M.

---

## Co-branding (Customer-side)

By default, the PDF shows only LedgerProof Foundation branding. Customers on the Production-tier and above may add their own logo to the top-right of the header band, replacing the QR code position; the QR code moves to the footer-center.

Customer logos are reviewed once at first co-branding setup. No Customer logo is added without a signed co-branding agreement.

---

## Companion artifacts

- **Stamp CBOR specification** — `spec.ledgerproofhq.io/stamp-cbor`
- **Stamp verifier source code** — `github.com/ledgerproof/stamp-verifier` (Apache 2.0)
- **Example stamp** — `verify.ledgerproofhq.io/stamp/example` (real stamp for the Foundation's own AI usage)
- **Regulator briefing document** — `docs.ledgerproofhq.io/regulator-briefing.pdf` — what a regulator should know before reading their first stamp
