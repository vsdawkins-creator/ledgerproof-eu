# LPR-VER-001 — Protocol Versioning Policy v1.0

| Field | Value |
|---|---|
| Policy ID | LPR-VER-001 |
| Status | Active |
| Effective | 2026-07-06 (public launch) |
| Author | LedgerProof Foundation |
| Permanent URL | `spec.ledgerproofhq.io/versioning-v1` |
| Backward-compatibility commitment | Ten (10) years from issuance of any LPR major version |
| Reviewed by | Technical Steering Committee (TSC) on ratification, Day 90 |

## Purpose

Document the Foundation's commitment on how the LedgerProof Protocol evolves over time, what changes are permitted within a major version, what changes require a new major version, and how customers can rely on receipts they issue today still verifying ten years from now.

This document is published BEFORE a customer or regulator asks "what happens to my 50,000 receipts when you ship v1.2?" — it is the answer they get when they ask.

## Versioning scheme

LedgerProof Protocol versions follow the form `LPR major.minor[.patch]`:

- **Major** — breaking changes to wire format or semantics. New major versions get a new OP_RETURN magic-bytes tag (current: `LPR1` → next: `LPR2`). Major-version receipts and prior-major-version receipts coexist on Bitcoin; verifiers must continue to recognize all previously published major-version tags.
- **Minor** — additive changes only. New fields, new profiles, new content types. Old receipts always verify under new readers. New receipts never break old readers (unless the old reader opts in to strict-mode rejection of unknown fields, which is documented but non-default).
- **Patch** — non-protocol changes (clarifications, errata, documentation improvements). Patches do not change the receipt format or verification algorithm.

Current version: **LPR 1.1**. Next planned: **LPR 1.2** (additive Code-of-Practice profile system; ratified by TSC by Day 90; deployed to production by Day 90). Future: **LPR 2.0** (post-quantum hybrid Ed25519+ML-DSA-65; RFC by Day 180; deployed 2028).

## OP_RETURN tag policy

The Bitcoin OP_RETURN payload prefix is the formal identifier of the major protocol version:

| OP_RETURN prefix | Status | Coexistence policy |
|---|---|---|
| `LPR1` | Active (current) | Recognized by all verifiers v1.0+ indefinitely |
| `LPR2` | Reserved (future) | Will coexist with `LPR1` indefinitely; v2.0 verifiers MUST recognize `LPR1` |
| `LPR3+` | Not reserved; available for future use | — |

The OP_RETURN prefix MUST NOT change within a major version. Renaming `LPR1` to anything else is structurally a major-version bump and triggers a new tag.

## Backward-compatibility commitment

The Foundation commits that any receipt issued under LPR `1.x` will be verifiable by any LPR `1.x` verifier for at least 10 years from the date of receipt issuance. This commitment is independent of whether LedgerProof Inc. continues to operate; the verifier source code is Apache 2.0 and Foundation-maintained.

When LPR `2.0` is published, the v2.0 verifier MUST verify v1.x receipts using v1.x rules. This is enforced in the verifier reference implementation's CI test corpus, which retains every published v1.x receipt as a regression test.

## Additive evolution within a major version

Within `LPR 1.x`, the following changes are permitted as minor-version increments:

1. **New optional fields** on existing entry / receipt / signature objects.
2. **New content types** (new `content_type` values for the `content` object).
3. **New profiles** — the LPR profile system permits the Foundation to publish new "profiles" that mark specific receipts as conforming to a specific regulatory or contextual schema (e.g., `article-50-1`, `dora-28`, `mifid-ii-16`, `iso-42001-a-6-2-8`). Profiles are additive metadata; they never modify the verification algorithm.
4. **New mappings** — new published mapping documents at `spec.ledgerproofhq.io/mappings/`.
5. **New errata** — published at `spec.ledgerproofhq.io/errata/` and `pre-v1-entries` register updates.

The following changes are NOT permitted as minor-version increments:

- Renaming or removing existing fields
- Changing the SHA-256 hash algorithm (would require LPR 2.0)
- Changing the Ed25519 signature algorithm (would require LPR 2.0)
- Changing the canonicalization rules in any way that affects existing receipts' verification
- Adding mandatory fields whose absence breaks v1.0 verifier expectations
- Changing the OP_RETURN payload format

## Profile system

The Profile system is the additive evolution path for LPR `1.x` to accommodate regulatory clarity as the EU AI Act Code of Practice is finalized, DORA RTS land, etc.

A receipt MAY include a `profile` field naming one or more profiles it claims to conform to:

```json
{
  ...
  "profile": ["article-50-1", "dora-28"],
  ...
}
```

Each profile is documented as `LPR-PROFILE-<name>-<version>` at `spec.ledgerproofhq.io/profiles/`. A profile MAY require specific fields in the `content` or metadata layer; conformance to a profile is checked by the verifier as an additive check (failing profile conformance does not fail the receipt's underlying integrity verification).

Profiles are non-mutually-exclusive. A receipt may conform to multiple profiles simultaneously.

The Foundation TSC ratifies new profiles. Third parties (regulators, industry groups, customers) may propose profiles; the TSC review process is documented at `spec.ledgerproofhq.io/profile-process`.

## Pre-v1.0 receipts (the special case)

Receipts issued before LPR 1.0 was finalized (May 6–17, 2026) are flagged in the canonical registry with a `pre_v1` marker. Verifiers handle them per `LPR-ERRATA-001`. The Foundation does not commit to verification correctness on these entries; their content is preserved on the chain for forensic purposes only.

The `pre_v1` register is published at `spec.ledgerproofhq.io/pre-v1-entries.json` and mirrored at `ledgerproof-verifier/public/pre-v1-entries.json`. The two files MUST stay in sync; CI enforces this.

## Deprecation policy

When a field, profile, or behavior is deprecated within a major version:

1. **Announcement** — published at `spec.ledgerproofhq.io/deprecations/` with deprecation date.
2. **Soft deprecation period** — minimum 24 months. Both old and new continue to work; SDKs emit warnings.
3. **End-of-life** — after the soft deprecation period, the deprecated item may be removed in the next major version (not within the current major version).

No item present in LPR 1.0 will be removed within the LPR 1.x line.

## Errata policy

Errata are published at `spec.ledgerproofhq.io/errata/` with sequential `LPR-ERRATA-NNN` IDs. Each errata is anchored as a LedgerProof receipt itself; the errata register is dogfooded.

The current errata register (as of issuance):

- `LPR-ERRATA-001` — Entry #0 stored content_hash mismatch (pre-v1.0 publisher draft artifact); status: documented, contained, no protocol change required.

## Migration paths between major versions

When LPR `2.0` is published:

1. Operators MAY continue to issue LPR `1.x` receipts under the same OP_RETURN tag indefinitely.
2. New LPR `2.0` receipts use the new OP_RETURN tag `LPR2`.
3. Existing customers MAY migrate to LPR `2.0` at their own cadence; LPR `1.x` receipts already issued continue to verify forever.
4. The migration document for `1.x → 2.0` will be published as `LPR-MIGRATION-2.0` at `spec.ledgerproofhq.io/migrations/` no less than 12 months before the LPR `2.0` deployment date.

For the planned LPR `2.0` (post-quantum hybrid):

- Receipts can carry both Ed25519 and ML-DSA-65 signatures (dual-sign)
- v2.0 verifiers verify both signatures
- v1.x verifiers verify only the Ed25519 signature and ignore the ML-DSA-65 field as unknown-optional
- Customers can migrate signing infrastructure at their own pace through the transition period
- The transition period ends only when the Foundation TSC declares Ed25519 deprecated, no sooner than 5 years from LPR 2.0 deployment

## Stability commitments

The Foundation commits that:

1. **`LPR1` magic bytes never change** within the LPR 1.x major version.
2. **Receipt format additions are always optional** unless and until a new major version is declared.
3. **The verifier's set of mandatory checks** (entry exists, entry hash, content hash, publisher key, Ed25519 signature, receipt anchor) does not change within LPR 1.x.
4. **The Bitcoin chain is the source of truth** for receipt anchoring; no other chain or sidechain substitutes for Bitcoin within LPR 1.x.
5. **GDPR Article 17 soft-delete posture** does not change within LPR 1.x without a published errata.

## Foundation TSC voting

Versioning decisions are made by the Foundation Technical Steering Committee (TSC). TSC composition:

- Three seats: Foundation chair (Veronica Dawkins until Foundation Executive Director hires; rotates per Foundation governance docs), Inc. CTO of Protocol (target hire Day 60), one independent (target: Henry de Valence or Jameson Lopp).
- Quorum: 2 of 3.
- The independent seat has explicit veto on any breaking change.
- All TSC decisions are published as receipts on the canonical chain and anchored to Bitcoin.

## Change request process

To propose a versioning change:

1. Open an issue at `github.com/ledgerproof/ledgerproof-spec` titled `[VER-PROPOSAL]`.
2. The TSC triages within 30 days.
3. Accepted proposals enter a 30-day public comment period.
4. After comment period, the TSC votes; outcomes are published.
5. Accepted minor changes ship in the next `LPR 1.x` minor release.
6. Accepted breaking changes are bundled into the next major release (`LPR 2.0` or later).

---

**This versioning policy is the Foundation's commitment to customers, regulators, and other operators about how the protocol evolves. It is published before contracts are signed so that no procurement conversation needs to ask "what if the protocol changes?" — the answer is here.**

Issued June 1, 2026 by the LedgerProof Foundation
Ratified by the Foundation Technical Steering Committee (target: Day 90)
