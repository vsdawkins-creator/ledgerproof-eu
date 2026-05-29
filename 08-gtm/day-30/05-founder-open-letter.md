# Founder Open Letter — Public Launch (July 6, 2026)

**Publication channels:** ledgerproofhq.io homepage hero placement; LinkedIn long-form post from Veronica's account; PDF version anchored as a LedgerProof Receipt and added to the verifier portal as the canonical launch artifact

**Length target:** 800–1000 words. Long enough to be substantive; short enough to be read end-to-end.

**Tone:** Plain English. No marketing register. No "we believe." Statements of fact and statements of intent, both verifiable.

---

# What we built, and why we are giving it away

By Veronica S. Dawkins, Founder
July 6, 2026

In 27 days, the European Union's AI Act enters its first enforcement window. From August 2, every chatbot, every synthetic media generator, every AI-generated piece of content deployed at scale in the European market must be disclosed under Article 50. The Code of Practice that will guide enforcement has not yet been finalized. The companies responsible for compliance — and the regulators responsible for enforcement — are about to do something neither side has done before, at a scale neither side has tried, with a deadline neither side controls.

I started LedgerProof in early 2026 because I thought the technical layer needed for Article 50 — an audit trail that a regulator could verify without trusting the company being audited — did not exist. It still does not, in any form that meets a serious regulator's standard. The closest things are GRC platforms (which produce reports the regulator must trust), content watermarking schemes (which can be stripped), and bespoke audit logs (which can be rewritten). None of them survive contact with a determined examiner.

So we built one. Today the LedgerProof Protocol is live in production. It has been operating continuously since May 18. The first 50,000 receipts have been issued and are independently verifiable against Bitcoin mainnet. The protocol is published as an IETF Internet-Draft (`draft-dawkins-scitt-ai-article50-00`) and confirmed on the IETF Datatracker. The SDK is on PyPI and npm. The verifier portal is at `verify.ledgerproofhq.io` and verifies any receipt in under 10 seconds.

We are giving the protocol away. The specification is open. The reference implementation is Apache 2.0. The Foundation that governs the protocol — the LedgerProof Foundation, currently in formation as a US 501(c)(3) with Swiss and Singapore twins arriving in Q1 2027 — accepts any organization that wants to run a receipt-issuing operator on the same membership terms. LedgerProof Inc., the Delaware company I founded to operate the EU service, is one of those members. It has no equity claim on the protocol. If LedgerProof Inc. fails, the protocol survives. If a competitor operates a better service, customers can migrate without re-issuing a single receipt.

I want to explain why an open protocol was the only design that could work.

**Regulators do not trust vendors.** They cannot, for structural reasons. A regulator who endorses a closed protocol is endorsing a specific commercial party. A regulator who endorses an open protocol with a governing Foundation is endorsing a verification mechanism. The first is a procurement decision; the second is a policy decision. Article 50 enforcement needs the second.

**Enterprises do not trust vendors either, when the stakes are this high.** A General Counsel at a Tier-1 EU bank is not going to bet a €35M Article 99 fine on a Series A startup's continued solvency. The same GC will bet on a protocol governed by a Foundation, with multiple operators, with an open specification, and with the ability to self-host if everyone else disappears. We are building the technical answer to a question that GCs are asking out loud: "what happens if this vendor fails?"

**The Code of Practice will change.** No one knows exactly what the final Code will say. Anyone who claims certainty is bluffing. The protocol is designed with a profile system — when the Code specifies a new disclosure obligation, we publish a new profile, and existing receipts remain valid under their original profile while new outputs flow into the updated one. The Foundation governs which profiles are canonical. Customers do not have to re-paper their AI deployments every time the regulatory text moves.

What we have proven so far: a real protocol can ship before a regulatory deadline. A startup can operate the production service that uses it. Regulators can verify the output without taking our word for anything. Enterprises can deploy the SDK in a week. The audit trail problem has a buildable answer.

What we have not yet proven: that the protocol can scale to the European Union's full AI deployment footprint by August 2. That the Foundation can attract the second, third, and fourth operators it needs to be credibly independent. That the Big-4 firms, the cloud hyperscalers, and the national regulators will engage with the open-protocol framing the way they engaged with similar frameworks in past compliance windows (HIPAA, PCI-DSS, GDPR). These are open questions, and the next six months will answer them.

I want to thank the people who got the protocol to the launch:

The seed investors who closed in June — Mark Beeston at Illuminate Financial, the partners at TVP, Stillmark, and Fulgur Ventures — for committing capital to a Foundation-first structure that does not optimize their own returns. The IETF SCITT working group for reviewing the draft on a short timeline. The early enterprise pilots who agreed to deploy a five-week-old protocol on real production pipelines. The Future of Life Institute for building the EU AI Act assessment tooling that the rest of us reference. The Bitcoin developers whose two-decade-old work is the trust anchor underneath everything we ship.

And the regulators — at the EU Commission, at DG-CNECT, at the national competent authorities — who have not yet seen our briefing, but who will. Our job from this moment forward is to make Article 50 enforcement easier on the regulator side, not harder. That is the test the next year of this work will pass or fail.

The 10-second proof we exist: `verify.ledgerproofhq.io/r/founding-declaration`. Anchored to Bitcoin block [block_height] on May 18, 2026. Independently verifiable. No trust required.

We will see you at enforcement.

—

Veronica S. Dawkins
Founder, LedgerProof Foundation
veronica@ledgerproofhq.io
