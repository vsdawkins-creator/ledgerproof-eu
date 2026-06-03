# Harrison Chase / LangChain — Partnership Outreach (Tue Jun 2 / Wed Jun 3, 2026)

**To**: Harrison Chase — harrison@langchain.dev (or harrison@langchain.com if dev doesn't resolve)
**Cc (optional, V's call)**: Erick Friis — erick@langchain.dev (LangChain VP Eng / OSS lead); Bagatur Askaryan — bagatur@langchain.dev (LangChain co-founder)
**From**: Veronica S. Dawkins — veronica@ledgerproofhq.io
**Subject**: LangChain + LedgerProof — open Article 50 evidence layer; the adapter ships today
**Send window**: Tue Jun 2 PM PDT OR Wed Jun 3 09:30 PDT (= 12:30 ET = morning for Harrison, who is San Francisco-based)
**Attachment 1**: `15-protocol-distribution/adapters/langchain-python/` (pointer to GitHub once we split it out — for today, the launch-repo URL works)
**Attachment 2**: One-page joint Article 50 crosswalk diagram (suggested — see below for content; V can ask me to render as PDF)

---

Harrison —

I'm reaching out about a specific complementary integration between LangChain and the open-protocol work the LedgerProof Foundation has been shipping. The pitch in one sentence: LangChain handles AI orchestration. LedgerProof gives that orchestration the externally-verifiable Article 50 evidence layer LangSmith structurally can't produce. The integration code already exists.

**Brief on us.** LedgerProof Foundation is a US 501(c)(3) public charity in formation (Delaware, Adler & Colvin counsel) with a Dutch Stichting EU subsidiary in formation (Amsterdam, NautaDutilh counsel). The Foundation stewards an open cryptographic protocol that emits signed receipts for AI-touched interactions, Merkle-batches them, anchors the roots to Bitcoin mainnet via OP_RETURN. Verification is offline — Bitcoin chain + protocol public key + receipt — no SaaS in the verifier's path. The IETF SCITT-track Internet-Draft `draft-dawkins-scitt-ai-article50-00` is on the Datatracker. Foundation governance receipt-anchored. Today the Foundation filed a substantive consultation submission with the EU AI Office on the draft Article 50 Guidelines. Reference implementation in Python, TypeScript, and Rust under Apache 2.0.

**Why this matters for LangChain specifically.** Your AI Act crosswalk in the May post addresses Articles 9, 12, 13, 14, 15, 72 through LangSmith's tracing and HITL primitives — directly and credibly. Article 50 is the one article you (correctly) didn't claim. The structural reason is real: Article 50 transparency obligations are owed to *external* parties — supervisory authorities (CNIL, BaFin, AGCOM) and natural persons — and the evidence has to survive the deployer's continued operation, the vendor's continued operation, and any single jurisdiction's hostility. A vendor-tenant trace is the wrong shape. A Bitcoin-anchored cryptographic receipt is the right shape. That's the gap.

**The adapter.** We shipped `ledgerproof-langchain` today as a working Phase 1 MVP — Apache 2.0, pip-installable, with `LedgerProofCallbackHandler` (BaseCallbackHandler subclass), `lpr_receipt_node` (LangGraph node decorator for editorial-review workflows), three receipt schemas (`chatbot_session/v1` for Article 50(1), `generated_content/v1` for Article 50(2), `human_review/v1` for Article 50(4)). Stream-aware signing (no body buffering). Side-channel emission (never modifies LangChain response payload). 28 tests passing. Repo: github.com/vsdawkins-creator/ledgerproof-eu/tree/main/15-protocol-distribution/adapters/langchain-python.

**What I'm asking for** is a 30-minute conversation about a reciprocal integration:

1. A LangChain Cookbook entry that demonstrates the adapter end-to-end (we can co-author; we ship the code, you ship the surface)
2. A joint blog post — co-authored, published same day on both blogs — framed as "The Article 50 evidentiary stack: LangChain + LedgerProof." Your customers get a credible Article 50 story you don't have to build yourselves. We get reach into the LangSmith customer base.
3. Optional: LangChain Hub listing once we're past v0.1 hardening

What I'm explicitly NOT asking for: any commercial entanglement, any equity, any cross-promotion that suggests LangChain Inc. endorses LedgerProof beyond the integration itself. The Foundation operates under strict C1-C8 discipline — we don't claim regulator endorsement, we don't claim Article 40 presumption of conformity, we don't claim vendor partnerships we don't actually have. Co-publication that says exactly what each product does is the strongest credibility move both ways.

**Timing context.** EU AI Act Article 50 enforcement begins August 2 (60 days from this email). Whatever integration we land before then becomes part of the EU enterprise's compliance story for the first enforcement quarter. Whatever lands after has to fight against whoever moves first in the space — and Truera/Arize/W&B are the realistic candidates if they decide observability + Article 50 is a defensible adjacency.

I'm at veronica@ledgerproofhq.io. Calendly: [V to insert]. Happy to come on with our spec-lead on the LangChain side — Erick if he's the right person on integration, otherwise whoever owns the LangChain OSS surface.

If the partnership doesn't make sense from your side, please tell me directly so I can stop thinking about it as a path. Either way, the adapter is open-source under Apache 2.0 and will ship to PyPI this week regardless — the partnership question is about co-publication, not about whether the integration exists.

Thank you, Harrison.

Veronica S. Dawkins
Founder, LedgerProof Foundation (in formation) · LedgerProof Inc.
veronica@ledgerproofhq.io · +1-XXX-XXX-XXXX
spec.ledgerproofhq.io · github.com/ledgerproof
IETF: `draft-dawkins-scitt-ai-article50-00`

---

## Suggested attachment — one-page Article 50 crosswalk diagram

If V wants me to render this as a PDF on Foundation letterhead (same tool we used for the consultation submission), say the word. Content:

```
ARTICLE 50 SUB-OBLIGATION       | LANGCHAIN PRIMITIVE              | LEDGERPROOF ADAPTER RECEIPT SCHEMA
================================|==================================|=====================================
50(1) Direct user disclosure    | BaseCallbackHandler.on_llm_start | chatbot_session/v1
                                | (capture disclosure context)     |
--------------------------------|----------------------------------|-------------------------------------
50(2) Synthetic content marking | BaseCallbackHandler.on_llm_end   | generated_content/v1
                                | (capture content hash)           | (out-of-band marking complements
                                |                                  |  in-band watermarking)
--------------------------------|----------------------------------|-------------------------------------
50(3) Emotion/biometric class.  | BaseCallbackHandler.on_llm_start | emotion_classification/v1 (v1.2)
                                | (capture system-class metadata)  |
--------------------------------|----------------------------------|-------------------------------------
50(4) Editorial control + text  | LangGraph.interrupt + resume edge| human_review/v1
                                | + lpr_receipt_node decorator     |
--------------------------------|----------------------------------|-------------------------------------
50(6) Manner of disclosure      | LangChain UI integration         | disclosure_text_hash field
                                | patterns                         | in chatbot_session/v1
```

Two layers: LangChain owns the orchestration plane. LedgerProof Foundation owns the evidence plane. Neither replaces the other.

---

## Operator notes (NOT part of the sent email)

**Why this email vs the longer version I drafted last week.** Last week's version was structured around the strategic case for the partnership. This version leads with the adapter exists today, which is materially stronger now that we've shipped the working code. The strategic case becomes the second paragraph instead of the first.

**Why I left contact for Erick + Bagatur optional.** Harrison-only is the cleanest first touch. CCing the co-founders signals seriousness but also pressure. V's call.

**Why no Calendly link.** V needs to insert her actual Calendly URL before sending. Don't auto-paste a generic one.

**Phone number placeholder.** Same as the audit firm emails — V fills in her real number.

**Why I named Truera / Arize / W&B in the closing.** Honest competitive pressure framing. Harrison is sophisticated about category dynamics; mentioning specific likely-competitors signals we understand the landscape. The implicit message: "you can be the LangChain that ships this in time, or you can be the LangChain that someone-else's-Article-50-story is built on."

**Why the "tell me directly if it doesn't make sense" close.** Harrison is direct. He responds to founders who don't dance. Inviting a "no" is what unblocks an honest "yes." Sales 101 for direct founders.

**Pre-send checks for V:**
- [ ] Verify Harrison's email — is it `harrison@langchain.dev` or `harrison@langchain.com`? Check his LinkedIn signature or last public talk slides.
- [ ] Decide whether to CC Erick + Bagatur (recommend: hold for second-touch if Harrison hasn't responded by Day +5)
- [ ] Fill in Calendly URL + phone number
- [ ] Decide whether to attach the PDF crosswalk now or hold for the call (recommend: include in email body as ASCII table above; offer the PDF on the call)
- [ ] Verify the GitHub URL — currently `github.com/vsdawkins-creator/ledgerproof-eu` (the launch monorepo). Once the Foundation `github.com/ledgerproof` org has a dedicated adapter repo, update.

**Day +5 follow-up (Mon Jun 8, 09:00 PDT) if no response:**
> Harrison — following up on the Article 50 / LangChain note from Tuesday. No urgency on your end; I know your inbox volume. Wanted to flag that the adapter is now installable via `pip install ledgerproof-langchain` (just hit PyPI), in case that simplifies a quick eval on your side before any partnership conversation. If a 15-minute call is easier than a 30-minute one for the first touch, that works too.
> 
> Either way, thank you for the work LangChain has done on the AI Act crosswalk — the May post is the cleanest analysis of what an orchestration framework actually owns under each article that I've read this year.
> 
> — Veronica
