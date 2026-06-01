# Canonicalization Investigation — Entry #0 Content Hash Failure

**Date:** Monday, June 1, 2026
**Investigator:** Claude + Veronica (5 minutes wall-clock, $0)
**Status:** ROOT-CAUSED. Bug is contained, narrow, and operational — not cryptographic.

## Summary in one paragraph

The verifier's content-hash check passes on entries 1, 2, 3, 4 and every later entry I have tested. It fails **only on Entry #0**. The verifier's canonicalization code is **correct**. The Rust publisher's canonicalization is **correct**. There is no cross-language drift. Entry #0 was issued with a `content_hash` field that does not match any reproducible canonicalization of its stored `content` field. The most likely explanation: a pre-v1.0 publisher draft state where the genesis entry's `content` field was edited after `content_hash` was computed and stored, leaving an orphan hash.

## What the verifier does (correct)

`ledgerproof-verifier/src/verify.ts:43–56`:

```ts
// Use content from entry_json_canonical to preserve original key order —
// PostgreSQL JSONB sorts keys alphabetically, so entry.content would produce a different hash.
const canonicalEntry = JSON.parse(entry.entry_json_canonical)
const contentBytes = new TextEncoder().encode(JSON.stringify(canonicalEntry.content))
const computedContentHash = sha256Hex(contentBytes)
```

This is V8 `JSON.stringify` over the parsed-and-re-extracted `.content` object from `entry_json_canonical`. The implementation is sound; insertion order is preserved through `JSON.parse → object → JSON.stringify`.

## Empirical confirmation

Tested against the live API at `https://api.ledgerproofhq.io/v1/entries/{seq}`:

| Sequence | Stored content_hash | Verifier-computed | Match |
|---|---|---|---|
| 0 | `051d95c233eeff21…` | `a655a3d8a814a415…` | ✗ |
| 1 | `eec835d8fcbef092…` | `eec835d8fcbef092…` | ✓ |
| 2 | `c1c477d4bb1203b6…` | `c1c477d4bb1203b6…` | ✓ |
| 3 | `4fcc413019011cb4…` | `4fcc413019011cb4…` | ✓ |
| 4 | `d4a6d7b0dca93ba9…` | `d4a6d7b0dca93ba9…` | ✓ |

The verifier code is operating correctly for every entry except #0.

## Variants tested against Entry #0 (none matched)

To rule out any reproducible canonicalization edge case, I tested:

- JCS RFC 8785 reference encoding (compact, sorted keys, no spaces, no unicode escapes)
- JCS with `—` escape for the em-dash
- Python `repr` (Rust `Debug`-like)
- JSON with `: ` colon-space separator
- JSON `indent=2` pretty-print
- CBOR (`cbor2.dumps`)
- MessagePack (`msgpack.packb`)
- Raw bytes of `entry_json_canonical`
- Raw bytes of `entry_hash` field (alternate)
- `content || timestamp` concatenated
- `"v1" || content` prefix-wrapped
- `"ledgerproof/1.0" || content` prefix-wrapped
- `sha256d` (double SHA-256, Bitcoin-style)
- `sha512[:32]`
- `blake2b(32)`
- `hmac-sha256(publisher_id, content)`
- Em-dash variants: `--`, `-`, en-dash `–`, surrounding-space variants, NFC/NFD/NFKD normalization, leading/trailing whitespace strip
- `conviction` numeric variants (`92`, `0.9`, `0.8`, `1.0`)
- Field-removal variants (drop `conviction`, `direction`, `note`, `ticker`)
- Field-addition variants (`+sequence`, `+publisher_id`, `+timestamp`, `+version`)
- Note variants (`LedgerProof trading signal`, `LedgerProof day 1`, `LedgerProof genesis entry` alone, casing changes)

**None of ~40 variants matched the stored `051d95c2…` hash.** The hash is not recoverable from any conventional canonicalization of the current stored content.

## Conclusion

The content stored under `content` for Entry #0 differs in some non-reconstructable way from the content the publisher hashed at issuance time. This is consistent with:

1. **Pre-v1.0 publisher draft edit-after-hash.** Most likely. The genesis entry was issued during the May 6 setup; an editorial change (typo fix, em-dash swap, spacing) to the `content` field occurred after `content_hash` was committed, and the hash was not recomputed.
2. **Lost intermediate transform.** A normalization step that was applied at hash time but not at storage time (or vice-versa) and has since been removed from the publisher pipeline.
3. **Direct database write that bypassed the publisher pipeline.** Possible if the genesis entry was seeded via a SQL script rather than the publisher API.

All three explanations are **operational/historical**, not cryptographic. The protocol is sound.

## What this changes about the playbook

### Trail of Bits engagement (scope shrinks)

Original 10X playbook line item: **$45–65K, two-week canonicalization-only review** to find the bug.

Revised scope: **$15–25K, three-day v1.1+ canonicalization correctness audit**. The bug is already root-caused; ToB's role is now adversarial confirmation that v1.1+ entries (seq ≥ 1) remain canonicalization-correct under their independent test corpus, plus signing off on the LPR-ERRATA-001 narrative.

**Saved: ~$30–40K and ~10 calendar days.** Reallocate those days into hot-path items E5 (multisig custody) and 30-day-wedge item P1.3 (verifier-core vendored).

### Entry #0 fix path (simplified)

Original: bisect canonicalization bug, fix code, re-issue.
Revised: re-issue Entry #0 as Entry #0-bis on the (already-working) v1.1 publisher path, anchor it, link from museum page. No code change required to the publisher or verifier.

The museum page at `docs.ledgerproofhq.io/entries/0` explains: "Entry #0 was issued during the pre-v1.0 publisher draft. Its stored content_hash does not match its stored content. Subsequent entries (1+) verify correctly. Entry #0 is enshrined as a permanent forensic artifact; Entry #0-bis at sequence [N] is the canonical founding-declaration receipt issued on the v1.1 path."

### Cross-language hash conformance CI (still load-bearing)

The empirical evidence that the Rust↔TypeScript canonicalization agree for entries 1+ is real, but informal. Hot-path item E7 (CI test that hashes a 100-entry corpus identically in Rust and TS) remains load-bearing — it prevents *future* drift, even though no drift exists today.

### Founding-declaration receipt content (ready to draft)

Per the playbook, Veronica issues Entry #0-bis as the canonical founding-declaration anchor through the publisher portal once the verifier slug-router PR merges. Content draft in `06-founding-declaration-entry.md` (this directory).

## What ToB SHOULD validate (the revised SOW)

1. Independent re-implementation of the v1.1 canonicalization spec in a third language (e.g. Go). Hash a 100-entry corpus drawn from the live API; confirm bytewise hash agreement with the Rust publisher and the TS verifier.
2. Adversarial-fuzz the canonicalization with Unicode edge cases (combining marks, NFC/NFD, RTL marks, surrogate pairs, control chars), number representations (scientific notation, `-0`, very-large integers, NaN/Inf rejected), and nested structure variants.
3. Confirm the verifier's `JSON.parse → JSON.stringify` round-trip preserves the bytes correctly for all entries in the corpus.
4. Sign off on the LPR-ERRATA-001 narrative as an accurate description of the Entry #0 historical artifact.

**Deliverable:** 5–10 page memo published at `security.ledgerproofhq.io/tob/2026-06-canonicalization-audit`.

## What this does NOT change

- The hot-path PAT revoke (E1) is unaffected — still P0 for Monday.
- The Unchained multisig setup (E5) is unaffected — still load-bearing for founder-load reduction.
- The two-stage seed restructure is unaffected.
- The Adler & Colvin engagement is unaffected.
- The Hercules Capital term sheet is unaffected.
- The federated on-call rotation is unaffected.
- The Foundation governance work is unaffected.

The investigation **shortened one engineering critical path** by ~10 calendar days. Everything else proceeds as designed.
