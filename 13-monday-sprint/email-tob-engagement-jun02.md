# Trail of Bits — Engagement Email (Jun 2, 2026)

**To**: Dan Guido — dan@trailofbits.com
**Cc**: engagements@trailofbits.com
**From**: Veronica S. Dawkins — veronica@ledgerproof.org
**Subject**: LPR v1.1 cryptographic protocol — engagement request (Article 50, Aug 2 enforcement)
**Send window**: Tue Jun 2 08:15-08:25 PDT
**Attachment**: `14-seed-close-pack/02-threat-model-briefing.md`

---

Dan —

I'm reaching out about an audit engagement on a deeply specialized cryptographic protocol with a hard regulatory deadline. We need Trail of Bits specifically because the work that matters most lives at the Rust + canonical-encoding + RFC 8032 strict-mode + Merkle proof layer — your craft zone.

**LedgerProof Protocol (LPR) v1.1** is the open IETF SCITT-track protocol (`draft-dawkins-scitt-ai-article50-00`) that anchors AI Article 50 transparency receipts to Bitcoin via a 36-byte `LPR1 || merkle_root_32` OP_RETURN payload. EU AI Act Article 50 enforcement begins Aug 2, 2026. Foundation publishes the audit memo by Aug 31 — that memo is the gate for IETF SCITT WG adoption, CEN-CENELEC JTC 21 standing, and Big-4 regulator engagement.

**Why Trail of Bits, specifically:**

We have three parallel scopes going to three firms. The Trail of Bits scope is the one I'm most directly asking you to take, because the work is closest to your team's reputation:

1. **Cross-language canonicalization correctness.** Rust (`quantum-edge-2`) + Python (`ledgerproof` 1.1.1rc0) + TypeScript (`@ledgerproof/sdk` 1.1.1-pre.0) all must produce byte-identical canonical encodings of LPR entries. Adversarial RCA on `LPR-ERRATA-001` (publishing Entry #0 as a pre-v1.0 artifact surfaced an off-by-one canonical encoding difference between languages — now contained but a representative class of bug). We have ~40 variant test vectors we generated in a 5-minute investigation; we want your team to extend the matrix and find what we missed.

2. **Ed25519 RFC 8032 strict-mode invariants.** We use `@noble/ed25519` 2.3.0 (pinned — 3.x has breaking API changes). Strict-mode behavior on canonical-encoding violations, non-canonical S values, low-order points. Confirm we reject every malleability vector RFC 8032 §8.5 lists.

3. **Merkle proof boundaries.** RFC 6962-style trees with `LPR1`-prefixed leaves. Proof verification correctness; depth limits; empty-tree handling; single-leaf handling; duplicate-leaf handling.

4. **Bitcoin OP_RETURN reorg behavior.** The 36-byte `LPR1 || merkle_root_32` payload is inviolable. Reorg windows, confirmation depth thresholds, RBF interactions, OTS fallback transitions.

5. **Rust compiler optimization paths.** Constant-time invariants in the Rust signing path under `-C opt-level=3`; integer-overflow behavior in the canonical-encoding hot loop; `no_std` boundary correctness in the embeddable verifier.

**What I'm not asking you to scope (going to other firms):**
- HSM integration patterns + stream-aware signing pipelines + Merkle-batch boundaries → NCC Group
- SDK black-box and white-box fuzzing + slug-router authorization → Cure53

**Budget framework:** $80-120K for the full v1.1 protocol scope as detailed above. 3-week fieldwork window. Memo finalization by Aug 24; publication target Aug 31 on `security.ledgerproofhq.io/tob/2026-08-canonicalization-audit`.

**Timeline ask:**
- Engagement-letter response by **Fri Jun 5, EOD ET** (kill-switch for our Aug 31 publication target)
- Kickoff call week of Jun 8
- Fieldwork Jun 8 → Jul 29
- Draft memo Aug 1
- Final memo Aug 24
- Public publication Aug 31

The threat-model briefing attached covers six-component system architecture, full STRIDE matrix per component, the LPR-ERRATA-001 RCA, and the ten special drill targets I'd want you to validate.

I'm available for a 30-min kickoff call this week — Wed Jun 3 or Thu Jun 4, any time PT. If your team isn't the right fit for the scope as framed, please tell me directly; I'd rather know Fri Jun 5 than chase a fit that isn't there.

Thanks Dan.

Veronica S. Dawkins
Founder, LedgerProof
veronica@ledgerproof.org · +1-XXX-XXX-XXXX
spec.ledgerproofhq.io · github.com/ledgerproof
