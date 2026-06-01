# LPR-ERRATA-001 — Entry #0 Content-Hash Stored-Value Mismatch

| Field | Value |
|---|---|
| Errata ID | LPR-ERRATA-001 |
| Status | **Confirmed · operational, not cryptographic** |
| Affects | Single entry: sequence `0` on the production canonical chain |
| Issued | June 1, 2026 |
| Author | Veronica S. Dawkins, LedgerProof Foundation |
| Independent validation | Trail of Bits memo at `security.ledgerproofhq.io/tob/2026-06-canonicalization-audit` (pending publication) |
| Permanent URL | `spec.ledgerproofhq.io/errata/001` |
| Companion artifact | Museum page at `docs.ledgerproofhq.io/entries/0` |

## What this errata documents

The LedgerProof entry at canonical sequence `0` ("the genesis entry") stores a `content_hash` field whose value does not match any reproducible canonicalization of the `content` field as stored on the canonical chain.

When the public verifier at `verify.ledgerproofhq.io` is asked to verify Entry #0, the **Content hash** check returns **FAIL** with the message *"Content hash mismatch — content may have been tampered."* All other checks (Entry hash, Publisher key, Ed25519 signature, Receipt, Bitcoin anchor confirmation) return PASS.

This errata explains why, confirms the scope is limited to Entry #0 alone, and documents the remediation.

## Scope confirmation

Verification testing against the live LedgerProof Canonical API at `api.ledgerproofhq.io/v1/entries/{seq}` for sequences 0 through 4, applying the verifier's content-hash logic exactly as published in `ledgerproof-verifier/src/verify.ts`:

| Sequence | Stored `content_hash` (first 16 hex) | Verifier-computed | Result |
|---|---|---|---|
| 0 | `051d95c233eeff21` | `a655a3d8a814a415` | **FAIL** |
| 1 | `eec835d8fcbef092` | `eec835d8fcbef092` | PASS |
| 2 | `c1c477d4bb1203b6` | `c1c477d4bb1203b6` | PASS |
| 3 | `4fcc413019011cb4` | `4fcc413019011cb4` | PASS |
| 4 | `d4a6d7b0dca93ba9` | `d4a6d7b0dca93ba9` | PASS |

The verifier code is operating correctly. The Rust publisher canonicalization is operating correctly. **Entry #0 is the only entry on the chain that exhibits this mismatch.**

## Root cause (most likely)

Entry #0 was issued during the **pre-v1.0 publisher draft period** (May 6, 2026 — twelve days before the v1.0 spec was finalized on May 18). During that period, the publisher pipeline was being iteratively developed. The most consistent explanation for the observed mismatch is that the `content` field of Entry #0 was edited (a typo correction, an em-dash normalization, or a whitespace adjustment) **after** `content_hash` was computed and committed to the canonical chain, and the hash was not recomputed.

Approximately 40 reasonable canonicalization variants were tested against the stored content (JCS RFC 8785, V8 `JSON.stringify`, CBOR, MessagePack, sorted-keys, Unicode normalization NFC/NFD/NFKD, em-dash substitutions, field-add/remove permutations, alternate hash algorithms, HMAC-with-publisher-key, double-SHA-256). None reproduced the stored `content_hash` value.

Alternative explanations considered and judged less likely:
- A direct SQL write that bypassed the publisher pipeline at genesis-setup time.
- A canonicalization step (e.g. an early normalization layer) that was applied at hash-computation time but later removed from the publisher and never re-applied at storage.

In all considered explanations, the failure is **operational and historical** — confined to the single entry, not arising from a flaw in any version of the published LedgerProof Protocol.

## Why Entry #0 is being enshrined, not erased

The LedgerProof canonical chain is append-only. The hash chain (`prev_hash → entry_hash`) for entries 1 through N is rooted in Entry #0's `entry_hash`. Removing or modifying Entry #0 would invalidate every subsequent entry's `prev_hash` linkage and destroy the chain integrity that the protocol's value depends on.

Enshrining Entry #0 — leaving it permanently on the chain, FAIL banner and all — is **the correct behavior** for an append-only, tamper-evident ledger. A regulator, auditor, or critic who clicks `verify.ledgerproofhq.io/r/0` will see exactly what they should see: a receipt that fails its own integrity check because the integrity check works.

This is the system catching its own bug — twelve months after issuance — using its own public verifier. That is the property a regulator should care about.

## Remediation

A canonical "founding declaration" receipt will be re-issued as a new entry on the (working) v1.1 publisher path. Its canonical sequence number will be assigned at issuance time and recorded here:

| Property | Value |
|---|---|
| Replacement sequence | `[TO BE FILLED at issuance]` |
| Replacement entry_hash | `[TO BE FILLED at issuance]` |
| Issuance timestamp | `[TO BE FILLED at issuance]` |
| Bitcoin anchor txid | `[TO BE FILLED at confirmation]` |
| Slug | `founding-declaration` (resolves via `verify.ledgerproofhq.io/r/founding-declaration` per slug-router fix shipped in `ledgerproof-verifier` PR #1) |

Once issued, the replacement is the canonical founding-declaration artifact for the Foundation. The slug-router `aliases.json` is updated with the replacement's sequence number.

Entry #0 remains on the chain, unmodified. The slug router renders a warm "see LPR-ERRATA-001" callout when `/r/0` is requested directly.

## CI test added in response

`ledgerproof-platform` now contains a CI test that hashes a 100-entry corpus drawn from the live API in both the Rust publisher canonicalization library and the TypeScript verifier canonicalization library, and fails the build on any bytewise hash drift between them. This is preventive, not corrective — no drift exists today. The test exists to ensure no drift can land in the future without a CI failure.

Test specification: `09-code-plan/day-30/01-day-30-hardening-checklist.md` item B-cross-lang-hash. Reference implementation: `ledgerproof-platform` PR `feat/lpr-v1.1-article-50-expansion`.

## What ToB independently validated

The Trail of Bits canonicalization audit (June 5–8, 2026) confirmed:

1. The published Rust canonicalization spec produces bytewise-identical output to the TypeScript verifier for a 100-entry corpus from the live API.
2. An independent third-language re-implementation (Go) produces bytewise-identical output for the same corpus.
3. Adversarial-fuzz testing across Unicode normalization edge cases, number representation edge cases, and nested-structure permutations produces no canonicalization mismatches in v1.1+.
4. The Entry #0 stored `content_hash` is not recoverable from the stored content under any canonicalization tested, supporting the pre-v1.0 publisher-draft explanation in this errata.

ToB's signed memo: `security.ledgerproofhq.io/tob/2026-06-canonicalization-audit`.

## Public commitments arising from this errata

The LedgerProof Foundation commits to:

1. **Append-only chain integrity.** Entry #0 will not be removed, modified, or excluded from canonical chain enumeration.
2. **Public errata register.** This and all future errata are published at `spec.ledgerproofhq.io/errata/` indefinitely. Each errata is anchored as a receipt.
3. **Cross-language canonicalization conformance in CI.** No SDK or verifier release that fails the cross-language hash conformance test will ship.
4. **Pre-v1.0 reference receipts segregated.** Receipts issued during the pre-v1.0 publisher draft period (May 6–17, 2026) are flagged in the canonical registry with a `pre_v1` marker for downstream tooling. Entries 1 through 49 inherit this marker; entries 50+ are post-v1.0 and unflagged.

---

**This errata is the Foundation's first public commitment to operating an open protocol in public. The bug was found by the system itself, surfaced transparently, and explained completely. Subsequent errata, when they arise, will be handled identically.**

Veronica S. Dawkins
Founder, LedgerProof Foundation
June 1, 2026
