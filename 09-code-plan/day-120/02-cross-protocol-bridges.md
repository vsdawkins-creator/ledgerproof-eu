# Cross-Protocol Bridges — C2PA, SCITT, OpenTimestamps

**Purpose:** Avoid forcing customers to choose between LedgerProof and other transparency / provenance ecosystems. By Day 120, customers should be able to publish a LedgerProof Receipt that **references** a C2PA manifest, a SCITT entry, or an OpenTimestamps anchor — and our verifier portal surfaces the cross-references without claiming authority over the other protocol.

**Owner:** Spec Lead
**Target spec inclusion:** LPR v1.2 (the cross-protocol fields are already specified) — Day 60
**Target verifier support:** Day 120
**Target customer-facing UX:** Day 150

---

## Why bridges, not adapters

We are not converting between protocols. We are **co-issuing**: a customer produces a LedgerProof Receipt that contains a reference to (the hash of, or the identifier of) an artifact from another protocol. The other protocol's artifact is validated by that protocol's own verifier; we do not absorb its validation responsibility.

This is structurally important: each protocol's verifier is the authority for its own artifacts. If we tried to validate C2PA manifests inside our verifier, we would inherit C2PA's complexity and trust assumptions. We do not.

---

## The three bridges in scope for v1.2

### 1. C2PA bridge

**Use case:** A media organization generates an image with an AI tool. They attach a C2PA manifest documenting provenance. They also want a LedgerProof Receipt for Article 50(2) compliance.

**LPR v1.2 field:** `c2pa_manifest_hash` — SHA-256 of the canonical C2PA manifest. Verifier portal displays the hash; user clicks through to validate against a C2PA validator (link to verify.contentauthenticity.org or similar).

**No semantic validation by us.** We attest only to the hash binding — that the customer signed a receipt claiming this manifest existed at receipt issuance time. The manifest's own validity is C2PA's responsibility.

### 2. SCITT bridge

**Use case:** An enterprise has invested in IETF SCITT transparency infrastructure (e.g., a SCITT transparency service in their procurement supply chain). They want their LedgerProof Receipts to be findable from their SCITT entries.

**LPR v1.2 field:** `scitt_entry_id` — the identifier of the corresponding SCITT statement. The verifier displays the identifier and provides a lookup hint. The customer points to which SCITT transparency service runs the lookup.

This bridge matters strategically because LedgerProof and SCITT are in the same IETF family. Bridging at the field level signals to the IETF WG that LedgerProof is a good citizen of the broader SCITT ecosystem, not a competitor to it.

### 3. OpenTimestamps bridge

**Use case:** A customer wants additional independent timestamping on top of LedgerProof's Bitcoin anchor. They submit the receipt hash to OpenTimestamps for an independent Bitcoin anchor, then carry the OTS receipt alongside.

**LPR v1.2 field:** `opentimestamps_proof` — base64-encoded OTS proof. The verifier portal displays a "Verify via OpenTimestamps" button that runs the OTS verification client-side in browser (WASM build of the OTS library).

This is the cheapest of the three bridges to implement and provides defense-in-depth on timestamping for customers who want it.

---

## What the verifier portal does with a bridged receipt

For each cross-protocol field present:
1. Display the field with a clear "External Protocol: [name]" label
2. Show the bound value (hash, identifier, or proof)
3. Provide a one-click action to validate via the external protocol's tooling
4. Cache the validation result for 24 hours
5. Surface validation failures distinctly: "External validation failed — LedgerProof Receipt itself remains valid"

The user-facing UX makes clear that the LedgerProof Receipt's validity is independent of external validation results. A failed C2PA validation does not invalidate the receipt; it just means the customer's claim about the C2PA manifest is in question.

---

## Authorization model

A receipt may include any subset of the three bridge fields. Whether the bridge is meaningful depends on customer practice:

- A media customer signing C2PA manifests in their pipeline should populate `c2pa_manifest_hash`
- An FSI customer using SCITT in their procurement chain should populate `scitt_entry_id`
- Any customer wanting independent timestamping should populate `opentimestamps_proof`

Customers who use no other protocols leave all three fields null. The receipt remains valid.

**Foundation does not endorse specific external protocols beyond what's listed.** Customers may add `external_attestation_uri` for vendor-specific attestations (e.g., AWS Signer, Sigstore, etc.), but the verifier does not surface validation actions for arbitrary URIs.

---

## Architectural decisions documented

1. **Hash binding only, not content embedding.** We never embed a full C2PA manifest in a receipt. Manifests are large; embedding bloats receipts. The hash binding is the protocol-correct primitive.
2. **Client-side validation for external protocols.** OpenTimestamps validation runs in the user's browser, not on Foundation servers. This avoids the Foundation acquiring responsibility for the validation result.
3. **No automatic mutual issuance.** A LedgerProof Receipt does not auto-trigger a SCITT statement or a C2PA manifest. Customers issue each independently in their pipelines.
4. **Bridge fields are optional and additive.** No customer is required to use any bridge field. Receipts without bridge fields verify identically.
5. **Bridge field set is closed in v1.2.** Adding a fourth bridge in v1.3 is an additive spec change. We do not allow customers to invent ad-hoc bridge fields — that is what `external_attestation_uri` is for.

---

## What this unlocks commercially

For each bridge:
- **C2PA:** Unblocks media customers who have invested in C2PA. They no longer have to choose between C2PA and LedgerProof. They publish both.
- **SCITT:** Aligns with IETF SCITT WG and broader supply-chain transparency ecosystems. Customers using SCITT for software supply chain extend it to AI outputs via LedgerProof.
- **OpenTimestamps:** Defense-in-depth for security-conscious customers. Demonstrates we are confident in our own timestamping by encouraging external verification of it.

These bridges are referenced in the FSI sector whitepaper (Day 120 GTM artifact) as part of the "no vendor lock-in" story.

---

## Pre-launch gates

- [ ] Verifier portal renders bridge fields for all three protocols
- [ ] C2PA validation link uses a stable, Foundation-approved external validator URL
- [ ] SCITT lookup hint format documented in the spec
- [ ] OpenTimestamps WASM bundle ships with the verifier portal
- [ ] Receipt with all three bridge fields is generated in CI and verified end-to-end
- [ ] FAQ for customers: "When should I use which bridge?"
- [ ] Acknowledgment from at least one C2PA implementer that the bridge field format is non-controversial

---

## Open questions

1. **Should the verifier portal cache external-protocol validation results in the Foundation Canonical Registry?** Trade-off: caching speeds repeated checks, but introduces a stale-cache problem if the external protocol's status changes. **Recommend no caching at the registry layer; client-side 24h cache only.**
2. **Should we support reverse-bridging — a SCITT statement that references a LedgerProof Receipt?** Yes, but that's the SCITT spec's responsibility, not ours. We document the LedgerProof Receipt identifier format so SCITT implementations can adopt.
3. **Multi-anchor receipts (Bitcoin + Ethereum + OpenTimestamps)?** Out of scope for v1.2. Revisit at v2.0 — multi-chain anchoring is on the research backlog.
4. **C2PA manifest size validation.** Receipts with `c2pa_manifest_hash` should we cap on the manifest size? **No — we only carry the hash; manifest size is the customer's problem.**
