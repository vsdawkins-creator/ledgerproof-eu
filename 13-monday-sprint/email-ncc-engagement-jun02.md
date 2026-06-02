# NCC Group — Engagement Email (Jun 2, 2026)

**To**: Marc Henderson — marc.henderson@nccgroup.com
**Cc**: engagements.us@nccgroup.com
**From**: Veronica S. Dawkins — veronica@ledgerproof.org
**Subject**: LPR v1.1 enterprise-architecture audit — engagement request (Article 50, Aug 2 enforcement)
**Send window**: Tue Jun 2 08:25-08:35 PDT
**Attachment**: `14-seed-close-pack/02-threat-model-briefing.md`

---

Marc —

I'm engaging three audit firms in parallel for an open AI-compliance protocol with a hard EU regulatory deadline. NCC Group is the firm I want for the enterprise-systems-architecture and infrastructure-security scope — the work that lives at the HSM integration + stream-aware signing + Merkle-batch boundary + production-deployment layer, which is your enterprise practice's craft zone.

**Background.** LedgerProof Protocol (LPR) v1.1 is the open IETF SCITT-track protocol (`draft-dawkins-scitt-ai-article50-00`) that anchors AI Article 50 transparency receipts to Bitcoin. EU AI Act Article 50 enforcement begins Aug 2, 2026; Foundation publishes the combined audit memo by Aug 31. That memo gates Foundation regulator briefings, IETF SCITT WG adoption, CEN-CENELEC JTC 21 standing, and Big-4 working-group engagement.

**Why NCC Group, specifically:**

Three parallel scopes, three firms. The NCC scope is what I'm most directly asking you to take, because enterprise-architecture review under production load is where your team's reputation lives:

1. **HSM integration patterns.** Enterprise deployments will sign receipts using AWS CloudHSM / Azure Dedicated HSM / on-prem Thales Luna / YubiHSM2. Per-request HSM signing is prohibitive at AI inference volumes (5-50ms signing latency × 100-10,000 req/s). We use a **Merkle-batch architecture**: N requests aggregate into one Merkle tree, the root signs once via HSM, individual receipts include inclusion proofs. We want NCC to validate the cryptographic correctness AND the operational-security boundary of this batching pattern (batch-window timing attacks, partial-batch failure modes, batch-root revocation if a per-leaf payload is later determined unsafe).

2. **Stream-aware signing for AI inference.** Many enterprise AI workloads are streaming (SSE / chunked HTTP). We cannot use Kong's `body_filter` phase (full-body buffering breaks streaming and adds 50-200ms p99 latency). We use a **stream-close signing** pattern: the signing happens on stream-end with a transcript hash committed at start. We want NCC to validate the integrity of this design — specifically the gap between stream-start commitment and stream-end signature (replay window, partial-stream attack, mid-stream key compromise).

3. **GDPR Article 17 erasure on a public ledger substrate.** Bitcoin OP_RETURN data is permanent. Our schema rejects emails / direct identifiers in `deployer_id`, `reviewer_role`, `review_rationale` (schema-level GDPR safety net). Erasure requests under Article 17 are handled via a soft-delete pattern: the entry remains in the Merkle tree, but its content is replaced with a tombstone marker; the anchored proof confirms erasure-by-the-deployer. We want NCC to validate that this pattern survives CNIL-style scrutiny on blockchain/GDPR compatibility.

4. **Bitcoin reorg + OP_RETURN persistence boundaries.** What confirmation depth do we require before treating an anchor as final? RBF (Replace-By-Fee) interactions during anchoring; OpenTimestamps fallback under network congestion; OP_RETURN payload-size policy boundaries (currently 80 bytes max; our payload is 36).

5. **Enterprise-deployment operational patterns.** Federated on-call rotation; key custody (Foundation 2-of-3 multisig anchor key + per-operator signing keys); chaos-engineering for anchor-stall scenarios.

**What I'm not asking you to scope (going to other firms):**
- Rust + canonicalization + Ed25519 strict-mode + Merkle proof correctness → Trail of Bits
- SDK black-box + white-box fuzzing + slug-router authorization → Cure53

**Budget framework:** $80-120K for the full v1.1 enterprise-architecture scope as detailed above. 3-week fieldwork window. Memo finalization Aug 24; combined audit memo publication Aug 31 on `security.ledgerproofhq.io/ncc/2026-08-enterprise-architecture-audit`.

**Timeline ask:**
- Engagement-letter response by **Fri Jun 5, EOD ET** (kill-switch for Aug 31 publication target)
- Kickoff call week of Jun 8
- Fieldwork Jun 8 → Jul 29
- Draft memo Aug 1
- Final memo Aug 24
- Public publication Aug 31

The threat-model briefing attached covers the six-component system architecture, the full STRIDE matrix per component, and the ten special drill targets. The briefing flags items 1-5 above as NCC-primary; items I've routed to ToB and Cure53 are labeled accordingly.

I'm available for a 30-min kickoff call Wed Jun 3 or Thu Jun 4, any time PT. If the scope doesn't fit your team's current bandwidth, please tell me directly Fri Jun 5 — I have a contingency path through Cure53 + Latacora that I'd need to activate immediately if NCC declines.

Thanks Marc.

Veronica S. Dawkins
Founder, LedgerProof
veronica@ledgerproof.org · +1-XXX-XXX-XXXX
spec.ledgerproofhq.io · github.com/ledgerproof
