# LangChain × LedgerProof Partnership Proposal

**To:** LangChain BD / Product (Harrison Chase, Ankush Gola; route via partnerships@langchain.dev or BD contact)
**From:** Veronica S. Dawkins, LedgerProof Foundation
**Date:** May 25, 2026
**Subject:** Closing the Article 50 gap in LangSmith — a partnership proposal

---

## TL;DR

LangSmith brilliantly addresses the high-risk AI system obligations of the EU AI Act (Articles 9–15). It does not address Article 50 (transparency for AI-generated content). LedgerProof is purpose-built for Article 50 — and is the only open protocol covering all four of its sub-obligations. A LangSmith + LedgerProof integration would let LangChain offer full EU AI Act coverage from one developer workflow, days before the August 2 enforcement date. We propose a partnership track to ship this in 30–45 days.

---

## What we observed

LangChain is actively spending paid search budget on EU AI Act keywords. Your landing page at `info.langchain.com/eu-ai-act` accurately positions LangSmith as compliance infrastructure for high-risk AI systems — observability, evaluation, human oversight, Articles 9–15.

That coverage is real, deep, and well-executed. It leaves one obligation untouched: **Article 50.**

Article 50 is the transparency obligation that applies to *deployers* of AI systems generating content (text, images, audio, video, synthetic media). It enforces August 2, 2026. Penalties: €15M or 3% of global turnover.

LangSmith's enterprise customers are the exact population this hits hardest: companies building AI-generated content workflows with LangChain. Every LangChain user generating customer-facing content under EU jurisdiction will need an Article 50 compliance record for each generation event.

LangSmith currently does not produce that record. We do.

---

## What LedgerProof is

LedgerProof Receipt (LPR) v1.1 is the only open protocol currently providing machine-readable cryptographic compliance records for all four Article 50 sub-obligations:

- 50(1) Interactive AI disclosure (chatbot sessions)
- 50(2) Synthetic media machine-readable marking
- 50(4) AI-generated text + human editorial review exemption

LPR receipts are:
- **Bitcoin-anchored** for permanent independent verifiability
- **GDPR-safe** by design (only hashes anchored, not content; soft-delete supported)
- **Open** (CC BY 4.0 specification, Apache 2.0 reference implementation)
- **IETF-submitted** as `draft-dawkins-scitt-ai-article50-00`
- **C2PA-compatible** via the `org.ledgerproof.receipt.v1` assertion mapping
- **eIDAS-compatible** for joint use with qualified electronic seals

The production EU deployment is live at `https://api-eu.ledgerproofhq.io` (Frankfurt, EU data residency).

We are 70 days ahead of the Article 50 enforcement date with three real Bitcoin mainnet anchors already on record.

---

## What the integration looks like

The integration is small in code and large in product value. Conceptually:

```python
from langchain.callbacks import LedgerProofCallback

callback = LedgerProofCallback(
    api_key=os.environ["LEDGERPROOF_API_KEY"],
    publisher_id="acme-corp-eu-deployment",
    deployer_id="LEI:5493001KJTIIGC8Y1R12",
    deployer_country="DE",
)

llm = ChatAnthropic(callbacks=[callback])
response = llm.invoke("Draft a press release about ...")

# Behind the scenes:
# 1. LangChain captures the LLM call as usual (LangSmith trace)
# 2. The callback hashes the response content
# 3. The callback issues an LPR ai/article-50/v1 receipt
# 4. The trace_id and receipt_id are cross-referenced in both systems
# 5. LangSmith displays the LPR receipt link inline in the trace UI
```

For human-in-the-loop workflows (the Article 50(4) editorial review exemption):

```python
@chain.with_human_review(reviewer_role="senior-editor")
def draft_pipeline(...):
    ...

# The decorator additionally issues an ai/human-review/v1 receipt
# referencing the original ai/article-50/v1 receipt by entry_hash,
# creating the cryptographic chain of custody for the 50(4) exemption.
```

For LangGraph agents with tool calls:

```python
agent = create_react_agent(model, tools, callbacks=[LedgerProofCallback(...)])
# Each tool call that produces user-facing content gets a receipt.
# The receipt content_type can be customized per tool.
```

The callback is ~400 lines of Python. We can write it.

---

## What we propose

### Phase 1 — Spike (2 weeks)

- LedgerProof writes the `langchain-ledgerproof` integration package
- LangChain provides a maintainer review for naming, callback API, and packaging conventions
- We jointly publish to PyPI as `langchain-ledgerproof` (or under your namespace if preferred)
- LangChain links from the EU AI Act page to a paragraph: "For Article 50 transparency obligations, see our LedgerProof integration"

### Phase 2 — Co-marketing (4 weeks)

- Joint blog post: "Full EU AI Act coverage with LangSmith + LedgerProof"
- LedgerProof becomes a "Recommended Integration" on the LangSmith integrations page
- LangSmith adds an Article 50 column to its compliance feature matrix that links to LedgerProof
- Joint webinar (60 min) on EU AI Act compliance for AI agent developers

### Phase 3 — Deeper integration (post-launch, optional)

- LangSmith trace UI displays LPR receipt status inline (green checkmark for "Article 50 receipt issued")
- LangSmith export formats include LPR receipt references in audit bundles
- Joint enterprise SKU: LangSmith + LedgerProof bundled for EU enterprise customers

### What we ask in return

- Engineering review time (5–10 hours of one engineer)
- Co-marketing alignment (joint blog post + webinar)
- "Recommended Integration" status on LangSmith
- A named contact for the partnership (we will reciprocate)

### What we offer

- All of the engineering on our side
- Open-source release of the integration (under permissive license)
- A "Founding Integration Partner" designation in LedgerProof launch materials July 6
- Charter pricing for LangChain enterprise customers using the integration ($499/month vs. $1,500 standard)
- Joint customer references for the EU enterprise GTM

---

## Why now

The EU Code of Practice finalizes in early June 2026. The Article 50 enforcement date is August 2, 2026. After August 2, every LangChain enterprise customer with EU exposure faces a compliance question without an integrated answer. After August 2, they will solve it themselves — likely with multiple separate vendors — and the integration window will be more crowded.

There is a 30–45 day window where a clean LangChain + LedgerProof partnership ships before the enforcement deadline, captures the narrative, and saves your enterprise customers the work of stitching together compliance vendors.

We can ship Phase 1 in two weeks from a partnership go-ahead. Phase 2 in four weeks. Phase 3 is post-launch and entirely optional from your side.

---

## Founder context (one paragraph)

LedgerProof is founded by Veronica S. Dawkins. The protocol has been in development since 2024, is live in production in Frankfurt, has three Bitcoin mainnet pre-launch anchors on record (most recent: May 18, 2026), and was independently audited by a senior Rust cryptography contractor (audit at `13-api-backend/CONTRACTOR-AUDIT-MAY24.md`, available on request). LPR is being shepherded into the IETF SCITT working group. Our launch is July 6, 2026.

We are in active conversations with Trammell Venture Partners (Christopher Calicott, Aryan Malhotra) for a $5M seed round. A LangChain integration partnership would materially affect both that round and your enterprise GTM.

---

## Next step

A 30-minute call with the right BD or product lead. I have time [propose three slots]. Or, if you prefer asynchronous: I am ready to share the integration package design doc and a Python prototype callback within 48 hours of a green light.

Reply to `founder@ledgerproofhq.io` or call [phone TBD]. I will respond same-day.

Sincerely,

Veronica S. Dawkins
Founder, LedgerProof Foundation
`founder@ledgerproofhq.io`

---

## Attachments (referenced, not required to read before the call)

- LPR v1.1 Specification: `04-lpr-spec/LPR-1.1-SPECIFICATION.md`
- IETF draft: `04-lpr-spec/IETF-DRAFT-DAWKINS-SCITT-AI-ARTICLE50-00.txt`
- C2PA assertion mapping: `04-lpr-spec/C2PA-ASSERTION-SPEC.md`
- eIDAS compatibility: `12-eu-compliance/07-EIDAS-COMPATIBILITY.md`
- Live production endpoint: `https://api-eu.ledgerproofhq.io/v1/health`
