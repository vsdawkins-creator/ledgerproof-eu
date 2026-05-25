# Pilot Pitch — Riot Games

**Delivered by:** Frank Gale (internal, Riot leadership)
**Targets:** Riot Trust & Safety leadership; Riot Legal/Compliance; Riot Player Dynamics
**Length:** One page

---

## The pilot in one sentence

Riot adopts the LedgerProof Receipt (LPR) protocol to anchor an auditable cryptographic trail of every AI-assisted player-behavior moderation decision Riot makes, beginning with a defined subset (proposed: chat-moderation appeals in LATAM-North) for the 90-day evaluation window.

## Why Riot, why now

Riot processes millions of AI-assisted moderation decisions monthly. The accuracy of those decisions is operationally critical and culturally consequential. When a decision is appealed, contested, or escalated to legal review, the evidentiary chain — what was said, what the AI flagged, what the human reviewer saw, what action was taken, in what order, at what time, signed by what process — is the asset that determines outcome.

In the next twelve months, three changes converge on this terrain:

1. **EU AI Act Article 50 enforcement (August 2, 2026)** requires machine-readable provenance on AI-generated content interacting with EU users. Riot's EU player base exceeds the regulation's threshold.
2. **Class-action litigation pressure** in the US is increasingly focused on automated moderation decisions affecting paid users. Plaintiffs' counsel will, beginning in 2026-2027, request auditable cryptographic trails of moderation decisions in discovery.
3. **Consumer regulator attention** (FTC, state AGs) on AI-driven consumer-facing decisions is accelerating.

LedgerProof provides Riot with a cryptographic audit trail that satisfies all three pressures at the same architectural level: every moderation decision, signed at the moment of execution, anchored to Bitcoin, verifiable by any external party (regulator, court, plaintiff's expert, internal auditor) without needing access to Riot's infrastructure.

## What the pilot would entail

- **Scope:** A defined moderation workflow (proposed: LATAM-North chat-moderation appeals) — bounded enough to evaluate, real enough to demonstrate value.
- **Integration:** LedgerProof, Inc. provides the SDK and API. Riot's team integrates against the existing moderation-decision pipeline. Estimated engineering: 2-4 weeks for first signal.
- **Cost during pilot:** Zero. LedgerProof, Inc. waives anchoring and SDK fees for the 90-day evaluation. The Foundation operates the verifier free for the world; Riot incurs no Foundation-side cost.
- **Outputs:**
   - Auditable receipt for every in-scope moderation decision (signed, anchored, verifier-link generated)
   - 90-day evaluation report: integration cost, latency overhead, false-positive verifier rate, qualitative legal/compliance assessment
   - Joint publishable case study (Riot approves all language; Foundation publishes nothing without Riot's written consent)

## What Riot would receive

- A working, verified, regulator-defensible cryptographic audit trail for the in-scope workflow.
- First-mover position in gaming-industry adoption of an open standard most peer companies (Activision, Epic, EA, Tencent, Microsoft Gaming) will face the same compliance pressure on within 12-18 months.
- A reference relationship with the open standard that will, on Frank's board judgment, define the documentary integrity layer for the next decade.
- The ability to truthfully state, in regulatory filings and litigation responses, that Riot's AI-assisted moderation decisions are cryptographically signed and publicly verifiable.

## What LedgerProof would receive

- A named launch pilot. The launch press cycle includes a sentence acknowledging Riot's evaluation. Riot reviews and approves the specific language.
- Real-world load on the production protocol. Riot's moderation volume is meaningful at LPR's anchoring tier.
- A reference customer in gaming and entertainment that opens the next set of conversations in the sector.

## Decision being asked

A 30-minute conversation with Riot Trust & Safety + Riot Legal/Compliance to confirm whether the 90-day pilot is feasible, scope-appropriate, and consistent with current Riot priorities. If feasible, contracting paperwork (a one-page joint pilot agreement) follows in the second 30-minute conversation.

— end —

> **FOUNDER ACTION REQUIRED:**
> 1. Frank reviews and adjusts framing to match the right Riot internal idiom before delivering.
> 2. The LATAM-North chat-moderation appeals scope is illustrative — Frank substitutes the workflow that is actually the right pilot at Riot.
> 3. The "named launch pilot" language is contingent on Riot's written approval. If Riot is not ready to be named publicly, the launch language degrades to "the Foundation is in evaluation conversations with a leading entertainment-industry partner" — Frank decides.
> 4. The pilot agreement is a contract; the licensed attorney reviews before Riot signs.
