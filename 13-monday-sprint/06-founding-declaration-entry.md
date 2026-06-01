# Founding Declaration Entry — Content for Publisher Portal Issuance

**Action:** Veronica issues this entry through the publisher portal at `publish.ledgerproofhq.io` once the verifier slug-router PR merges. The resulting sequence number is then written to `ledgerproof-verifier/public/aliases.json` under the `founding-declaration` key.

**Publisher ID:** `pub_b2aaabfc9e377bc0cd0149bd` (same as Entry #0 — preserves chain continuity)
**Key ID:** `key_6243966305e3d90f` (same as Entry #0)
**Content type:** `application/vnd.ledgerproof.foundation-declaration+json`
**Protocol version:** `ledgerproof/1.1`

## Content payload (JSON to paste into publisher portal)

```json
{
  "document_type": "founding-declaration",
  "title": "LedgerProof Foundation Founding Declaration",
  "issued": "2026-06-01",
  "version": "1.0",
  "issuer": {
    "name": "LedgerProof Foundation",
    "status": "in-formation",
    "jurisdictions": ["US-501(c)(3)", "CH-Verein-Q1-2027", "SG-NonProfit-Q1-2027"],
    "chair": "Veronica S. Dawkins"
  },
  "declaration": "The LedgerProof Foundation is established to govern the open LedgerProof Protocol (LPR) for cryptographic provenance of AI-generated content under EU AI Act Article 50 and adjacent regulatory regimes. The Protocol is specified at https://spec.ledgerproofhq.io. The Foundation operates the canonical registry, conformance suite, and Foundation-of-last-resort anchor. Multiple independent operators may issue LPR receipts; LedgerProof Inc. (Delaware) is one such operator and holds no equity in the Protocol itself. The Foundation commits to operate in public: every governance decision, errata, and transparency report is published openly and anchored as a LedgerProof receipt.",
  "protocol_invariants": [
    "Receipt format is append-only; new fields are additive.",
    "No PII at the anchor layer; schema rejection at parse time.",
    "No content data leaves the customer perimeter; only hashes and metadata.",
    "The verifier never depends on the operator; verification is possible with the public reference verifier and public Bitcoin chain alone.",
    "Versioned everything; every artifact has a version, deprecation policy, and migration path.",
    "Tamper-evidence dogfooding; Foundation publishes its own records as receipts."
  ],
  "first_errata_acknowledged": {
    "id": "LPR-ERRATA-001",
    "summary": "Entry #0 stored content_hash does not match stored content; pre-v1.0 publisher draft artifact; verifier code is correct; bug is contained to the single legacy entry; remediation is enshrinement, not erasure.",
    "url": "https://spec.ledgerproofhq.io/errata/001"
  },
  "supersedes_legacy_entry": {
    "sequence": 0,
    "entry_hash": "6810339213225906dbf322f9e6363e1384269ecea30bf9ae13a081582aec4084",
    "note": "Entry #0 remains on the chain as a permanent forensic artifact. This declaration is the canonical founding receipt issued on the v1.1 publisher path."
  },
  "public_commitments": [
    "Append-only chain integrity preserved across all errata.",
    "Independent cryptographic audits published at security.ledgerproofhq.io as they complete (Trail of Bits June 2026; Latacora supply-chain July 2026; Cure53 verifier August 2026).",
    "Bug bounty open at bounty.ledgerproofhq.io with €100K Foundation-funded pool by Day 90.",
    "Technical Steering Committee with independent veto seat operational by Day 90.",
    "Dutch Stichting registered as the EU contractual counterparty by September 30, 2026.",
    "Foundation board with three independent members seated by August 30, 2026."
  ],
  "verification": {
    "this_receipt_at": "https://verify.ledgerproofhq.io/r/founding-declaration",
    "spec": "https://spec.ledgerproofhq.io/lpr-1.1",
    "ietf_draft": "https://datatracker.ietf.org/doc/draft-dawkins-scitt-ai-article50/",
    "verifier_source": "https://github.com/ledgerproof/ledgerproof-verifier",
    "test_vectors": "https://github.com/ledgerproof/lpr-test-vectors"
  },
  "signed_by": {
    "name": "Veronica S. Dawkins",
    "role": "Founder, LedgerProof Foundation",
    "email_did": "did:web:foundation.ledgerproofhq.io",
    "date": "2026-06-01"
  }
}
```

## Issuance steps

1. Wait for `ledgerproof-verifier` PR #1 (slug routing + brand alignment) to merge — already opened.
2. Wait for the Entry #0 errata page at `spec.ledgerproofhq.io/errata/001` to be live (LPR-ERRATA-001 content is in `04-lpr-spec/LPR-ERRATA-001.md`; publication = push to spec site).
3. Sign in to `publish.ledgerproofhq.io`.
4. Create new entry. Paste content payload above. Confirm `content_type = application/vnd.ledgerproof.foundation-declaration+json`.
5. Submit. Record the assigned canonical `sequence` number.
6. Update `ledgerproof-verifier/public/aliases.json`:
   ```json
   {
     "founding-declaration": <sequence>,
     "0": 0
   }
   ```
   Commit + push to a new PR titled `data(aliases): map founding-declaration to entry [N]`.
7. Wait for Bitcoin anchor confirmation (target: ≤24h per fee-policy SLO).
8. Update LPR-ERRATA-001.md with the replacement sequence, entry_hash, anchor txid.
9. Update `04-10X-PLAYBOOK-MAY31.md` 7-day hot-path item 3 status → DONE.
10. Forward the live `verify.ledgerproofhq.io/r/founding-declaration` URL to the four co-leads as proof of Monday-sprint completion.

## What the regulator sees when they verify this receipt

When a regulator pastes `verify.ledgerproofhq.io/r/founding-declaration` into a browser, in under 10 seconds the verifier:

1. Resolves slug to sequence via `aliases.json`
2. Fetches the entry from `api.ledgerproofhq.io`
3. Re-computes entry_hash from canonical JSON → ✓ PASS
4. Re-computes content_hash from .content field → ✓ PASS (because issued on the v1.1 working path)
5. Fetches publisher key history; confirms the signing key was active at this sequence → ✓ PASS
6. Verifies the Ed25519 signature over entry_hash → ✓ PASS
7. Fetches the receipt; confirms anchor_status = confirmed → ✓ PASS
8. Fetches the Bitcoin transaction; confirms OP_RETURN payload matches Merkle root → ✓ PASS
9. Verifies confirmations ≥ 6 → ✓ PASS (after first day on chain)

All green. The content of the declaration is human-readable in the entry-details panel. The regulator can then click through to `spec.ledgerproofhq.io/errata/001` to read about the genesis entry's history, and to `bounty.ledgerproofhq.io` to see the Foundation's open security program. The "10-second proof we exist" is now an artifact that earns the regulator's respect, not just confirms a string.
