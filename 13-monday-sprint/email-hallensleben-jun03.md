# Sebastian Hallensleben — Outreach Email (Wed Jun 3, 2026)

**To**: Sebastian Hallensleben — sebastian.hallensleben@vde.com
**Cc**: (none — direct)
**From**: Veronica S. Dawkins — veronica@ledgerproof.org
**Subject**: LedgerProof Protocol — JTC 21 standards-track context + 30-min briefing request
**Send window**: Wed Jun 3, 09:30 PDT (= 18:30 CET — end-of-day in Frankfurt)
**Channel**: Email primary; LinkedIn DM as parallel touch with shorter version

---

Sebastian —

I'm reaching out because the LedgerProof Foundation (US 501(c)(3) in formation) is preparing to file for DIN SME membership this month with the explicit intent of contributing to CEN-CENELEC JTC 21's work on AI transparency standards. Before we file, I'd value 30 minutes of your time to brief you on the protocol approach and get your read on JTC 21 fit.

**Brief context.** LedgerProof Protocol (LPR) v1.1 is an open cryptographic protocol that anchors AI Article 50 transparency receipts to Bitcoin via a 36-byte OP_RETURN payload (`LPR1 || merkle_root_32`). The protocol is published as an IETF SCITT-track Internet-Draft (`draft-dawkins-scitt-ai-article50-00`, confirmed on Datatracker). Reference verifier is offline-capable; verification requires only Merkle proof + Ed25519 signature + Bitcoin chain headers — no dependency on any operator service. The Foundation publishes the spec, conformance test vectors, reference verifier, and IP license; LedgerProof Inc. is one of multiple permitted operators, not the IP owner.

EU AI Act Article 50 enforcement begins August 2, 2026 (60 days from this email). The Foundation's strategic position is that the protocol should evolve through European standards-track participation — IETF SCITT for the cryptographic mechanism, CEN-CENELEC JTC 21 for the European-context standardization needed to engage with the Article 40 harmonized-standards process under M/593.

**The specific ask.** Three things, in priority order:

1. **30-minute introductory call** (week of Jun 8 if your calendar allows, or whenever in the next 14 days works) to brief you on the protocol approach and discuss JTC 21 fit. Substantive, not pitch — I want your read on what's missing, what's wrong, and what would need to be true for JTC 21 to find a New Work Item Proposal credible.

2. **Feedback on Foundation-side sponsorship.** Once DIN membership is confirmed (target Q3 2026 post 6-8 week processing window), we'd intend to submit a JTC 21 NWIP. Your candor on whether the protocol approach has the technical substance to merit a NWIP — and what we'd need to strengthen before submitting — would be invaluable. I'd rather hear "this isn't ready" from you in June than hear it from JTC 21 in October.

3. **Discretionary**: if the protocol direction makes sense to you, connection to other JTC 21 members and national mirror committee delegates (DIN AK 043-01-42 AA on AI in particular). No pressure on this — only if the conversation in (1) and (2) lands.

**What I'm NOT asking.** I am not asking you to endorse the protocol publicly, to make any statement on JTC 21's behalf, or to advocate for inclusion. The Foundation's discipline is that European standards bodies are not vendors' endorsement machines — they are participatory processes. We want to do the work properly.

**Why I'm reaching out to you specifically.** Your work on the AI standards landscape — including the GPAI Code of Practice transparency chapter contributions and the CEN-CENELEC AI rapporteur role — makes you the single most qualified person in Europe to tell me whether what we're building has standards-track substance. Foundation board prospects (Mishi Choudhary, Allison Randal, Lokke Moerel) are aware I'm reaching out; happy to introduce on request.

The IETF Internet-Draft is at `https://datatracker.ietf.org/doc/draft-dawkins-scitt-ai-article50/`. The reference verifier and SDKs are at `github.com/ledgerproof`. The Foundation governance documents (Conflict of Interest Policy, IP Transaction Committee Charter, IP-license terms Inc.→Foundation) are in draft with Adler & Colvin counsel; happy to share under NDA if useful.

I have 30 minutes any morning Jun 8-12 (CET hours that work for you). Phone or video either way.

Thank you for your time, Sebastian.

Veronica S. Dawkins
Founder, LedgerProof
veronica@ledgerproof.org · +1-XXX-XXX-XXXX
spec.ledgerproofhq.io · github.com/ledgerproof
IETF: `draft-dawkins-scitt-ai-article50-00`

---

## LinkedIn DM (parallel touch, shorter version — send 09:35 PDT same day)

Sebastian — I just emailed you at sebastian.hallensleben@vde.com. LedgerProof Foundation is preparing a DIN SME membership filing this month with the goal of bringing a CEN-CENELEC JTC 21 NWIP on AI transparency cryptographic receipts (IETF SCITT-track, Bitcoin-anchored, offline-verifiable). Before we file, I'd value 30 minutes to brief you on the approach and get your honest read on JTC 21 fit. Article 50 enforcement Aug 2 makes the timing matter. If email is the wrong channel for this, please tell me your preferred path.

---

## Day +5 follow-up (send Mon Jun 8, 10:00 PDT if no response by EOD Sun Jun 7)

Sebastian —

Following up on the JTC 21 briefing request from Wed. No urgency on your end — I know your calendar this time of year is heavy with the GPAI Code-of-Practice and JTC 21 work. Two updates that may be relevant:

1. DIN SME application is now drafted; targeting filing Mon Jun 15.
2. We have ToB + NCC Group engagement letters returned (audit memo publication target Aug 31).

If a 15-minute call is more realistic than 30, that works too. If the right path is to talk again after we've published the audit memo, please tell me — I'll respect that and re-surface in September.

Either way, thank you for the work you do on JTC 21. The EU AI standards landscape benefits from your visibility on it.

Veronica

---

## Operator notes (not part of the email)

- Hallensleben is the single highest-leverage standards-track relationship we can cultivate. If his response is positive, the JTC 21 NWIP path opens substantially.
- His response may be slow (he is genuinely busy with the Code-of-Practice work). Day+5 follow-up should be polite, NOT pushy.
- If he responds positively and we get a call: lead with the IETF draft, then the IP license structure (Foundation owns spec; Inc. is one of multiple operators), then the audit. Hold the commercial story for later — he will trust the protocol-substance signal over the commercial-traction signal.
- If he responds with "this isn't the right time for JTC 21 to take on a new transparency NWIP" — DO NOT push back. Accept gracefully and ask what timing would be appropriate.
- DO NOT mention Article 95 voluntary codes as a "presumption of conformity" pathway. C1 hold. Article 95 is reputational only.
- DO NOT name specific Foundation board prospects in the Day+5 follow-up — they may not be confirmed yet.
- DO NOT name customer prospects (Riot, Klarna, etc.) — he's a standards person, not a commercial one. The protocol substance is what he cares about.
