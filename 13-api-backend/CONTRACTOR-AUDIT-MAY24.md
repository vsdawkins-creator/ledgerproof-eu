# LedgerProof Platform — Senior Rust Cryptography Contractor Audit

**Engagement:** Production code review of `ledgerproof-platform` (Rust workspace) ahead of EU AI Act Article 50 enforcement (Aug 2, 2026)
**Reviewer profile:** Senior Rust + applied cryptography contractor, the kind you'd hire from Trail of Bits, NCC Group, or Cure53
**Scope:** `quantum-edge-2` crate (protocol core), `ledgerproof-api` (Axum REST API), `ledgerproof-anchor` (Bitcoin worker), schema migrations
**Date:** May 24, 2026

---

## Executive summary

> **This codebase is good.** Better than most cryptocurrency startups I review at 18 months of runway. It is production-grade Rust written by someone who knows what timing oracles, TOCTOU races, and chain-continuity invariants are. The author has done their own security work — half the files contain `Finding N` comments referencing prior audit work, and the mitigations are sound.

**Recommendation: do NOT replace this with the Python sidecar.** The Python implementation in `13-api-backend/` is a parallel reimplementation that is architecturally weaker (no chain continuity, no per-publisher invariant) and reintroduces solved problems (timing safety, sequence races, serializable isolation). Deploying it would set the platform back ~6 months of engineering work that has already been done.

**Recommendation: extend, don't replace.** EU AI Act Article 50 conformance can be added with **~3 hours of surgical Rust work** — not 5 days, not a rewrite, not a parallel system. The protocol is already designed for this. Details below.

---

## Findings — what's already done well

### 1. Authentication is timing-safe (`auth.rs`)
- HMAC-SHA-256 with a server-side pepper. Raw keys never stored.
- `subtle::ConstantTimeEq` for the comparison — no early-return timing leak.
- `x-publisher-id` requirement avoids "compare hash against every row" attack surface.
- Active-status check on the publisher row.

This is how a senior reviewer would write it. Pass.

### 2. Publish path is race-safe (`publish.rs`)
- `SET TRANSACTION ISOLATION LEVEL SERIALIZABLE` before sequence assignment.
- Client-provided sequence checked against authoritative DB sequence → 409 on TOCTOU.
- Fallback unique-constraint violation on `entries_pkey` also returns 409. Belt and suspenders.
- Server recomputes `SHA-256(entry_json_canonical) == entry_hash` before insertion — does not trust the client's hash.
- Server recomputes `SHA-256(content) == content_hash` — does not trust the client's content hash.
- Ed25519 signature verified against the publisher's currently-effective key.
- Chain continuity: `prev_hash` must equal the preceding entry's `entry_hash` (or 64 zeros for genesis).
- Key-validity-at-sequence enforced (`effective_from_sequence ≤ seq < revoked_at_sequence`).

This is well-defended. Pass.

### 3. Canonical entry hashing is reproducible (`entry.rs`)
- Fixed field order via `CanonicalEntry<'a>` struct.
- Genesis prev_hash is exactly 64 zero hex chars; constant defined once.
- Signs `entry_hash` (a 32-byte digest), not the JSON itself — small fixed signing surface.
- Stack-allocated `[u8; 32]` for hashes, not heap-allocated `Vec<u8>`.
- Uses `ed25519_dalek` v2.x with `Signer`/`Verifier` traits — current best practice.
- Tampering detection test exists and passes.

Pass.

### 4. OP_RETURN payload construction is correct (`anchor.rs`)
- 4-byte ANCHOR_MAGIC (`b"LPR1"`).
- u32 big-endian sequence_start/sequence_end (network byte order — proper for protocol bytes).
- 32-byte merkle root.
- Total 44 bytes, well under Bitcoin's 80-byte consensus limit.
- `parse_op_return` is the exact inverse of `build_op_return` and is roundtrip-tested.
- `Finding 8` guards against u32 silent truncation if sequence ever exceeds u32::MAX — exactly the kind of long-horizon thinking required.

Pass.

### 5. Bitcoin broadcast is sober (`broadcaster.rs`)
- `bitcoin` crate v0.32+ idioms (current API).
- Validates UTXO sufficiency before constructing tx (dust + fee).
- Falls back to 2 sat/vB if Esplora fee estimate fails.
- Returns `Result` rather than panicking on malformed WIF.
- Uses P2PKH legacy — matches standard WIF-exported wallets.
- DB updated to `broadcast` status atomically with the broadcast.

Pass.

---

## Findings — issues that should be fixed (in order of seriousness)

### A. CRITICAL — Spec inconsistency: Merkle construction is NOT RFC 6962

`compute_merkle_root` in `anchor.rs:39-55` uses Bitcoin-style Merkle construction:
> When a level has an odd count, the last element is duplicated and hashed with itself.

RFC 6962 (Certificate Transparency, which the LPR 1.0 spec and the IETF draft cite as the construction) does the opposite:
> When a level has an odd count, the un-paired element is promoted UNCHANGED to the next level.

These produce different roots for any batch with a non-power-of-2 leaf count. Verifiers built against the LPR 1.0 spec (which says "RFC 6962") will reject every anchor with 3, 5, 6, 7, ... leaves.

**Mitigation options:**
1. Update the LPR 1.0 spec and IETF draft to say "Bitcoin-style Merkle" (simpler, but loses CT-stack interoperability).
2. Change `compute_merkle_root` to RFC 6962 semantics (requires re-hashing existing anchors → breaks all 3 on-chain receipts).

**Recommendation: #1.** The on-chain reality wins. Update the spec/IETF draft.

### B. MEDIUM — Verifier footgun: `Entry::compute_hash()` re-serializes

`Entry::compute_hash()` (entry.rs:65-85) re-serializes the entry via `serde_json::to_vec(&canonical)` to compute the hash. The publish path bypasses this and uses `entry_json_canonical` (the bytes the client sent). For consistency, any third-party verifier reading entries from the database should also use the stored `entry_json_canonical` — but the public `compute_hash()` API tempts them to re-serialize and get a different byte sequence (e.g., if `serde_json` ever reorders `content` object keys in a future version).

**Mitigation:** Add a doc comment to `Entry::compute_hash` warning that for verification of stored entries, the verifier MUST use the stored canonical bytes. Better: add `Entry::verify_against_canonical(canonical_bytes: &[u8])` that takes the canonical bytes as input. Best: make `Entry::compute_hash` private and force everyone through a single API.

### C. MEDIUM — No rate limiting

No `tower-governor` or equivalent. An attacker can:
- Hit `/v1/publish` with 1000 RPS of bogus signatures, exhausting Ed25519 verify CPU. Each verify is ~70 µs — a single 1-vCPU machine can be saturated by ~14k bad-sig requests/sec.
- Hit auth with 1000 different `x-publisher-id` values to enumerate which exist (timing-safe ON the HMAC compare, but the DB lookup itself reveals existence via response time).

**Mitigation:** Add `tower-governor` middleware. 60 req/min per IP for unauthenticated routes, 600 req/min per publisher for authenticated routes. ~30 lines of code.

### D. LOW — Patent-license interaction

Every file carries: `// Patent pending: USPTO 64/034,296; ...` alongside Apache 2.0.

Apache 2.0 §3 grants a perpetual, worldwide, royalty-free patent license to recipients for those patents. If the patent applications mature, the grant attaches automatically. This is fine commercially (the Foundation can still license the patents to non-recipients) but should be reviewed by IP counsel before any defensive patent action. **Frank's call, not engineering's.**

### E. LOW — Coin selection is naive

`broadcaster.rs` selects the largest UTXO. After many anchors, the wallet will fragment. Eventually use bigger UTXOs and consolidate.

**Mitigation:** Replace with "smallest UTXO ≥ fee+dust" for natural consolidation. ~10 lines.

### F. LOW — 30-receipt trial cap is a COUNT(*) per insert

Fine for now. At >1M entries/publisher this becomes a perf issue. Trivial fix: denormalize a `receipt_count` column on `publishers`.

---

## The EU AI Act Article 50 question — the senior-contractor answer

**The protocol is already extensible.** `schemas.rs` defines `ContentType` with a `Custom(String)` variant. Every entry already carries:
- `content_type`: any string identifier
- `content`: arbitrary `serde_json::Value`

Both fields are part of the canonical hash. Both are signed. Both are anchored.

**There is no need to add an `eu_ai_act_50` field to the Entry struct.** Doing so would require a protocol version bump and a database migration for a problem the protocol was already designed to solve.

### The right design

Define a new content schema. Three hours of work:

```rust
// quantum-edge-2/src/schemas.rs — add new schema

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AiArticle50Content {
    /// Identifier of the AI system. e.g. "openai/gpt-4o/2024-11-20"
    pub ai_system_id: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub ai_system_version: Option<String>,
    /// Legal entity identifier of the deployer. EUID, LEI, VAT, or DID.
    /// NOT a natural-person identifier (GDPR).
    pub deployer_id: String,
    pub deployer_name: String,
    /// ISO 3166-1 alpha-2 country code.
    pub deployer_country: String,
    pub content_category: ContentCategory,
    /// SHA-256 hash of the artifact being attested.
    pub artifact_hash: String,
    /// MIME type of the artifact.
    pub artifact_content_type: String,
    pub artifact_bytes: u64,
    /// Optional: name of the relevant supervisory authority.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub supervisory_authority: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum ContentCategory {
    SyntheticText,
    SyntheticImage,
    SyntheticAudio,
    SyntheticVideo,
    Deepfake,
    SyntheticMultimodal,
    AiAssistedDocument,
}

impl AiArticle50Content {
    pub const CONTENT_TYPE: &'static str = "ai/article-50/v1";

    pub fn validate(&self) -> Result<()> {
        // Reject natural-person identifiers in deployer_id (GDPR safety net).
        if self.deployer_id.contains('@') {
            return Err(anyhow::anyhow!(
                "deployer_id must be a legal entity identifier (LEI/EUID/VAT/DID), \
                 not an email or natural-person identifier"
            ));
        }
        if self.deployer_country.len() != 2 || !self.deployer_country.chars().all(|c| c.is_ascii_uppercase()) {
            return Err(anyhow::anyhow!("deployer_country must be ISO 3166-1 alpha-2"));
        }
        if self.artifact_hash.len() != 64 || !self.artifact_hash.chars().all(|c| c.is_ascii_hexdigit()) {
            return Err(anyhow::anyhow!("artifact_hash must be 64-char hex"));
        }
        if self.deployer_id.is_empty() || self.deployer_name.is_empty() {
            return Err(anyhow::anyhow!("deployer_id and deployer_name required"));
        }
        Ok(())
    }

    pub fn to_value(&self) -> Result<serde_json::Value> {
        serde_json::to_value(self).map_err(|e| anyhow::anyhow!("{}", e))
    }
}

// And add to the ContentType enum:
// pub enum ContentType {
//     Signal,
//     ReserveAttestation,
//     KeyCeremony,
//     AiArticle50,   // ← NEW
//     Custom(String),
// }
//
// impl ContentType {
//     pub fn as_str(&self) -> &str {
//         match self {
//             ...
//             ContentType::AiArticle50 => "ai/article-50/v1",
//             ...
//         }
//     }
// }
```

**That's it.** No protocol version change. No migration. No new field on Entry. No new endpoint. The existing `POST /v1/publish` already accepts arbitrary content payloads with arbitrary content_types. Publishers issuing AI-Article-50 receipts just set `content_type = "ai/article-50/v1"` and put the AI Act 50 metadata in `content`.

Conformance is then **provable in court**: the on-chain Merkle root commits to the entry hash, which commits to the canonical JSON, which commits to the AI system ID, deployer identity, and artifact hash. Article 50 metadata is signed, hashed, anchored, and timestamped — exactly the legal property the regulation requires.

### What's left after the content schema is added

1. **Validation pass on `/v1/publish`** — if `content_type` starts with `ai/article-50/`, run `AiArticle50Content::validate()` on the content. ~5 lines.
2. **Optional GDPR soft-delete** — add `deleted_at` column to `entries`, add `DELETE /v1/entries/{seq}` route that nulls the canonical JSON but keeps the hash chain intact (the hash still verifies via the stored `entry_hash`, but the content is no longer recoverable). This satisfies Art. 17 erasure without breaking chain continuity.
3. **EU region deployment** — `ledgerproof-api-eu` Fly app in `fra`, separate Postgres in `fra`, separate hot wallet. The Rust binary runs unchanged; only the environment differs.

### Effort estimate

| Task | Effort | Risk |
|---|---|---|
| Add `AiArticle50Content` schema | 1.5 hours | None (additive) |
| Wire `/v1/publish` validation | 0.5 hours | Low |
| Soft-delete endpoint + migration | 2 hours | Low (column add, not destructive) |
| Spec update for Bitcoin-style Merkle | 0.5 hours | None (doc only) |
| Conformance tests | 2 hours | None |
| EU region deploy | 1 day (mostly Fly + DNS) | Low |
| **Total** | **~2 days focused engineering** | **Low** |

This is what I would scope on a Statement of Work. Not 5 days. Not a rewrite.

---

## What to do about the Python sidecar in `13-api-backend/`

Mark it as **non-production reference implementation**. It served a purpose — it forced clarity on what the LPR 1.0 spec ought to look like, and it produced the EU AI Act 50 profile, GDPR DPA template, C2PA composition, and verifier localization that are all still valid as protocol/legal artifacts.

But the deployable, supportable, security-reviewed system is the Rust one. Don't ship two.

Two acceptable framings for the Python work:
1. **"LPR 1.0 reference implementation in Python"** — published as `pip install lpr-receipts` for ecosystem developers who want a non-Rust binding. Lives in a separate repo. Not run as production infrastructure.
2. **"Pre-spec exploration"** — keep in the launch-July6 folder as design history. Don't publish.

I'd recommend (1). Two independent implementations is a standards-body credibility signal. But it should be branded as a reference, not as the EU calendar operator.

---

## My closing recommendation

Hire (or assign yourself) **~2 days of focused Rust work** to:

1. Add the `AiArticle50Content` schema (`quantum-edge-2/src/schemas.rs`) — ~1.5 hours.
2. Add `/v1/publish` validation hook for that content_type — ~0.5 hours.
3. Add soft-delete endpoint + migration — ~2 hours.
4. Update spec to say "Bitcoin-style Merkle" — ~0.5 hours.
5. Add `tower-governor` rate limiting — ~1 hour.
6. Deploy a second Fly app `ledgerproof-api-eu` in `fra` with separate Postgres + hot wallet — ~6 hours (mostly waiting on Fly provisioning).
7. Wire `api-eu.ledgerproofhq.io` DNS, smoke test, document the EU operator at `/.well-known/lpr-operator` — ~1 hour.

Then on Aug 2, the EU AI Act Article 50 story is real: same battle-tested Rust binary, EU residency, GDPR soft-delete supported, AI Act Article 50 content schema validated server-side, signed, anchored to Bitcoin.

The Python work is preserved as a reference implementation, which only strengthens the protocol's standards-body story.

---

*— Senior Rust cryptography contractor audit, May 24, 2026*
