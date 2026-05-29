# Three Persona Cold Emails — CRO/CCO, Head of MLOps, General Counsel

**Purpose:** Stamped variants for the first wedge into a Tier-1 EU enterprise. Each email is calibrated to the persona's actual reading frame (see the three buyer skills in `~/.claude/skills/`).

**Send window:** Tuesday 09:00–10:30 CET. Avoid Mondays (inbox triage), Fridays (deferred to Monday). Never send before close on June 25 — wait until the public launch on July 6 to send to named-account targets.

**Subject-line rule:** No "Hope you're well." No "I noticed your background." No "AI safety" without Article 50. The subject must pass the 30-second test for that specific persona.

---

## Variant A — Chief Risk Officer / Chief Compliance Officer

**Subject:** Article 50 enforces in 67 days — what your CEO will ask on August 3

[First name],

The EU AI Act Article 50 enforcement date holds at August 2, 2026. The Omnibus extended high-risk AI systems to December 2027, but the transparency obligations on chatbots, synthetic media, and AI-generated content did not move. On August 3, your CEO will ask one question: "what is our exposure?"

The honest internal answer at most Tier-1 EU institutions today is: "we don't fully know what AI is deployed, and we don't have a defensible audit trail for the ones we do know about." That answer is what gets risk leaders escalated to the Board for the wrong reasons.

LedgerProof is an open cryptographic protocol that solves the audit-trail problem. Every AI output your organization produces is hashed, signed, and anchored to Bitcoin — making it independently verifiable by your regulator in 10 seconds, without trusting LedgerProof or any other vendor. Live in production since May 18. IETF Internet-Draft confirmed. Maps to 24 of 38 ISO/IEC 42001 Annex A controls and to DORA Article 28.

I am proposing a 30-day pilot on one bounded AI pipeline at [Company]. Flat $25K, MSA-light four-page SOW, fully creditable to any annual contract within 60 days. By Day 30 you have an Audit-Ready Compliance Stamp PDF you can hand to your Board.

Verifier (10-second proof we exist): https://verify.ledgerproofhq.io/r/founding-declaration

Open to 30 minutes any time in the next two weeks.

Veronica S. Dawkins · Founder, LedgerProof Foundation
veronica@ledgerproofhq.io

---

## Variant B — Head of MLOps / AI Infrastructure

**Subject:** SDK that adds <50ms P99 to your AI pipeline and produces Article 50 receipts

[First name],

You are the person who has to actually integrate whatever the compliance team buys. So I will skip the pitch and tell you the integration shape.

**LedgerProof SDK:**
- `pip install ledgerproof` or `npm install @ledgerproof/sdk`
- Wrap any model output → SDK computes SHA-256 + canonical CBOR locally, signs Ed25519, returns receipt
- Single HTTPS POST to EU operator (Frankfurt) — no content data leaves your perimeter, only the hash
- P99 latency overhead: ≤50ms (we contract to this in the pilot SOW)
- LangChain integration: `langchain-ledgerproof` 1.0.0 on PyPI
- Failure mode: SDK degrades to local queue + async retry; never blocks the inference path

**What the receipt is:**
- Open IETF-tracked format: `draft-dawkins-scitt-ai-article50-00`
- Anchored to Bitcoin mainnet via OP_RETURN (LPR1 prefix + 32-byte Merkle root, 36 bytes)
- GDPR-safe: schema rejects email addresses in `deployer_id` at parse time
- Verifiable by any third party without trusting LedgerProof

The protocol is open. Your team can self-host the operator if you prefer not to use ours. The Foundation will publish the reference implementation under Apache 2.0 in Q3.

I am proposing a 30-day pilot on one pipeline. The pilot SOW commits to specific latency and availability SLOs and refunds 100% if we miss either. Your compliance team gets a Board-ready PDF on Day 30. You get a working integration with documented runbooks.

Spec: https://spec.ledgerproofhq.io
GitHub: https://github.com/ledgerproof/ledgerproof-platform

Worth 30 minutes?

Veronica S. Dawkins · Founder, LedgerProof Foundation
veronica@ledgerproofhq.io · spec@ledgerproofhq.io

---

## Variant C — General Counsel

**Subject:** A Board Pack PDF for Article 50 — not a vendor pitch

[First name],

I have read enough Article 50 inbound to know how this normally goes: a vendor claims certain compliance with a Code of Practice that has not been finalized, you spot the bluff, and the conversation ends. So I want to put two things on the table that are actually useful to you.

**First:** A 30-minute Shadow AI Inventory engagement, free, no committed follow-up. Output is a PDF you can co-brand and hand to your CEO — a map of every AI system deployed at [Company], classified by Article 50 sub-clause and ISO 42001 control. You keep the PDF whether or not we ever do business.

**Second:** An honest acknowledgment that the EU Code of Practice is not finalized. LedgerProof's architecture adapts when the Code drops, because the receipt schema uses a profile system — when the Code specifies a new disclosure obligation, we publish a new profile, and your existing receipts remain valid under their original profile while new outputs flow into the updated one. Vendors who claim certainty about the Code today are bluffing.

LedgerProof is an open cryptographic protocol (IETF `draft-dawkins-scitt-ai-article50-00`), live in production since May 18, governed by a US 501(c)(3) Foundation in formation. The protocol generates regulator-grade receipts anchored to Bitcoin. We have an ISO/IEC 42001 mapping document covering 24 of 38 Annex A controls and a DORA Article 28 mapping covering ICT third-party risk evidence — both available before our first call.

I will come to the diligence call personally and answer regulatory questions without hand-off. Our 30-day pilot SOW is four pages, $25K flat, fully creditable. No MSA required.

Verifier (10-second proof we exist): https://verify.ledgerproofhq.io/r/founding-declaration

30 minutes in the next two weeks?

Veronica S. Dawkins · Founder, LedgerProof Foundation
veronica@ledgerproofhq.io

---

## Sequencing rules

1. **Never send all three to the same company on the same week.** Pick one entry point per account based on the public signal: if the company recently had a published CRO statement about AI, lead with Variant A; if the MLOps Head is active on technical channels, lead with B; if the GC is publicly speaking about AI governance, lead with C.
2. **If no response in 7 business days**, send a second variant to a different persona at the same company. Reference the first email with one sentence ("I also wrote to [name] last week — happy to keep both threads going or consolidate").
3. **If still no response in 14 business days**, switch to a written-only artifact send — the ISO 42001 mapping document or the Shadow AI Inventory one-pager, with a one-sentence note. No third "checking in" email.
4. **Never send more than two emails to the same person.** The third touch is always a different artifact or a warm intro.

## Subject-line A/B variants (for testing)

| Persona | Variant 1 (above) | Variant 2 (test) |
|---|---|---|
| CRO/CCO | "Article 50 enforces in 67 days — what your CEO will ask on August 3" | "[Peer institution] just deployed Article 50 receipts. Should [Company] be next?" |
| MLOps | "SDK that adds <50ms P99 to your AI pipeline and produces Article 50 receipts" | "Open-protocol Article 50 receipts — pip install ledgerproof" |
| GC | "A Board Pack PDF for Article 50 — not a vendor pitch" | "Shadow AI Inventory for [Company] — 30 minutes, no follow-up required" |

Use Variant 2 only after Variant 1 has been tested on at least 10 accounts and conversion rates are measurable.
