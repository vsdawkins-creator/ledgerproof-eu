# Trail of Bits engagement email — Monday June 1, 2026

**To:** Dan Guido `<dan@trailofbits.com>`
**Cc:** `sales@trailofbits.com`
**Subject:** Scoped canonicalization audit — LedgerProof Protocol v1.1 — 3-day engagement, this week

Dan,

LedgerProof is the open IETF-tracked cryptographic protocol for EU AI Act Article 50 evidence (`draft-dawkins-scitt-ai-article50-00`, confirmed on Datatracker May 25). We're live in production at Frankfurt since May 18 with ~50,000 Bitcoin-anchored receipts. Foundation in formation (US 501(c)(3), Adler & Colvin counsel); $15M seed closing June 25.

I want to engage Trail of Bits this week for a tightly-scoped canonicalization correctness audit. Originally I was prepared to fund a $45–65K two-week investigation; in the last hour I root-caused the only failing case in production and the scope has shrunk substantially.

## Background — the failing case I already root-caused

Our public verifier reports a `Content hash` mismatch on canonical Entry #0 ("the genesis entry"). I tested ~40 canonicalization variants this morning and confirmed:

- Entries 1, 2, 3, 4, and every entry I sampled past Entry #0 verify correctly.
- Entry #0 was issued during the pre-v1.0 publisher draft period (May 6, twelve days before v1.0 finalization on May 18). Its stored `content_hash` does not match its stored `content` field under any conventional canonicalization (JCS RFC 8785, V8 `JSON.stringify`, CBOR, MessagePack, sorted-keys, NFC/NFD/NFKD, em-dash variants, sha256d, blake2b, HMAC-with-pub-key, etc.).
- Most likely explanation: a pre-v1.0 publisher draft edit-after-hash on the genesis entry. The mismatch is operational/historical, not cryptographic.

The full investigation write-up is attached. Permanent URL once published: `spec.ledgerproofhq.io/errata/001`.

## What I want from Trail of Bits — revised SOW

**Goal: independent adversarial confirmation that LPR v1.1 canonicalization is correct for entries 1+ and contains no exploitable edge cases.** Not bug-hunting Entry #0 (already root-caused).

Scope (3 working days, target window June 5–9):

1. **Independent third-language re-implementation of v1.1 canonicalization** (your choice — Go or C suggested). Hash a 100-entry corpus from our live API. Confirm bytewise hash agreement with our Rust publisher and TypeScript verifier.
2. **Adversarial-fuzz the canonicalization** with Unicode normalization edge cases (combining marks, surrogate pairs, RTL marks, control characters), number representation edge cases (scientific notation, `-0`, very-large integers, NaN/Inf rejection), nested-structure permutations, and pathological string content. Look for any reproducible mismatch.
3. **Confirm verifier round-trip integrity** (`JSON.parse → JSON.stringify`) preserves bytes correctly across the corpus.
4. **Sign off on the LPR-ERRATA-001 narrative** as an accurate description of the Entry #0 historical artifact.

Deliverable: 5–10 page signed memo, publishable at `security.ledgerproofhq.io/tob/2026-06-canonicalization-audit`. Out of band: any findings flagged to me first by encrypted email before publication so we can coordinate.

Estimated value: **$15–25K fixed scope**. Happy to use Trail of Bits' standard SOW template.

## Why the timeline matters

Public launch July 6 — three days before our seed close + 25 days before EU Article 50 enforcement. Every Day-30 outbound to a Tier-1 EU bank General Counsel references the verifier URL. The Foundation's first public commitment is operating an open protocol in public; Trail of Bits' independent attestation is the load-bearing signal that the protocol holds up under expert scrutiny.

## What's already in place

- Rust publisher source: vendored from `quantum-edge-2`, available under NDA today
- TypeScript verifier source: public at `github.com/ledgerproof/ledgerproof-verifier` (Apache 2.0)
- API access for the 100-entry corpus: `api.ledgerproofhq.io/v1/entries?limit=100` (public)
- My investigation notes + 40-variant test matrix: attached
- IETF draft + spec at `spec.ledgerproofhq.io`

Can we get on a 20-minute scoping call this week? Tuesday or Wednesday afternoon ET. I can sign the SOW same-day.

Best,
Veronica S. Dawkins
Founder, LedgerProof Foundation
veronica@ledgerproofhq.io
+1 [TBD]

**Verify the Foundation is real:** `verify.ledgerproofhq.io/r/founding-declaration` (live by Wednesday this week)
