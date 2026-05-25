# Op-Ed — Wall Street Journal (target outlet)

**Author:** Veronica S. Dawkins, Founder, LedgerProof Foundation
**Target publication date:** July 1, 2026 (5 days before launch)
**Length:** ~1,150 words
**Working title:** *Three weeks from the AI Act, we still cannot prove a document is real*

---

In twenty-three days, the European Union's Artificial Intelligence Act begins enforcing Article 50, the provision that requires AI-generated content to be marked, in a machine-readable format, so any downstream system can detect that it was produced by a machine. The provision is short. The deadline is hard. The fines for noncompliance compound. And the consensus position of the European Commission's own Code of Practice on Article 50 marking — confirmed in writing in its March 2026 draft — is that no single marking technique currently in production satisfies the regulation. The phrase the Code uses is "no single active marking technique suffices."

I do not write this to alarm. I write it because the same sentence applies, with very minor edits, to every other domain in which the integrity of a document now matters: civil litigation, criminal evidence, regulatory disclosure, scientific publication, journalism, audit, insurance, loan origination, and the daily operation of every artificial-intelligence system whose outputs are now embedded in the consequential decisions made by every institution we depend on.

We can no longer prove a document is what it appears to be. We have known this for at least eighteen months. The regulation is the response. The response is necessary. It is also incomplete, and the gap it leaves open is the gap that frauds, errors, and manufactured records walk through.

I will describe the gap in plain language. Then I will say what I think the field needs to do, including what I have just done about it.

---

A document — a contract, a memo, a photograph, a regulatory filing, a paragraph of journalism, a court exhibit, the output of an AI model — exists today inside a custodial system. The custodial system is a database, a vendor's cloud, an enterprise file server, an agency archive. The custodial system can be modified. The custodian, or any insider with sufficient privilege, can change a date, change a sentence, change a signer, change the order of versions. Some custodial systems maintain audit logs. Audit logs can be edited by anyone who can edit the system. There is no party outside the custodian who can verify the document at issue — its existence at a moment in time, its authorship, the chain of its revisions — without trusting the custodian.

When the custodian is a publicly traded company under quarterly audit by a major firm, this is a tolerable condition because the auditors and the regulators apply pressure that, on average, keeps the custodian honest. When the custodian is a court clerk's office, this is a tolerable condition because the institutional culture of the judiciary keeps the custodian honest. When the custodian is a sovereign-state regulator, this is a tolerable condition for as long as the state is stable. When the custodian is none of these — when the custodian is a small enterprise, a startup, a vendor under financial pressure, a regime in transition, a system that no one outside the custodian audits — the condition is not tolerable. It is the condition that produces, every quarter, the wire-fraud losses now measured in billions of dollars, the evidentiary disputes that vacate criminal convictions, the corporate-records scandals that surface a year after the records were silently revised, and the regulatory enforcement actions that turn on document timestamps that no third party can independently verify.

This was a difficult condition before generative artificial intelligence arrived. Generative AI did not create the condition. It removed the last remaining heuristic — the assumption that a document showing characteristic human authorship was, in fact, produced by a human — that allowed the documentary economy to function despite the condition.

We are now in a documentary economy in which the question *is this document what it appears to be* is, by default, unanswerable by any party who does not trust the custodian. The default has changed. Most of the institutional response has not yet caught up. Article 50 is one step in that response. It is the most consequential step the regulatory world has taken so far, and the Code of Practice is right that it is not, alone, enough.

---

The class of technical solutions that can address this condition has been understood for at least a decade. The mathematics is not new. A document's content is hashed under a one-way cryptographic function. The hash is signed by the document's author with a public-key signature scheme. The signed object is aggregated into a Merkle tree alongside other signed objects produced in the same time window. The root of the tree is committed to a public ledger whose own integrity does not depend on any single party. Any future verifier — five years later, fifteen years later, fifty — can recompute the hash from the document, verify the signature against the asserted author's public key, verify the inclusion of the signed object in the Merkle tree, and verify the Merkle root in the public ledger. If all four checks pass, the document existed in that form, with that author's assertion, at the time the ledger committed the root.

The technique has been in production for a decade in a small number of specialized systems. It has not been adopted at the scale at which it is now required because, until very recently, the cost of being wrong about a document's authenticity was not high enough to overcome the cost of marking it. That ratio has now reversed. The cost of being wrong has become large enough, and visible enough, that the cost of marking — under an open standard, with free public verification — is the smaller of the two numbers.

What the field has lacked, and what the next twenty-three days require, is a published open specification that is plainly cryptographically sound, vendor-neutral, regulator-compatible, anchored on a public ledger whose continued operation does not require the survival of any one company, and free to verify. A standard, with a reference implementation, with the public verifier already operating, that a regulator can read, an auditor can assess, a court can accept, a journalist can use, and a procurement officer can specify.

This is the standard the LedgerProof Foundation released this morning, under Creative Commons, with reference implementations under the MIT license, with an Internet-Draft submitted to the IETF for community review, with a Bitcoin-anchored public verifier already operating, and with a founding board that includes counsel from the cryptographic community, academia, journalism, and finance. The full materials are at ledgerproofhq.io.

I do not claim that LedgerProof is the only acceptable approach. I do not claim that the LPR specification is the final word. I claim only that the documentary economy now requires an open Bitcoin-anchored cryptographic provenance standard, and that today there is one. Other standards will follow, and they should. The right response to the condition we are in is not for one institution to own the solution. It is for many institutions to converge on a small number of compatible open specifications, with free public verification, and with the regulatory frameworks now coming online to demand and accept them.

Twenty-three days from now, the European Union begins enforcing the first such framework. The cost of a document we cannot verify is no longer hypothetical. The cost of marking one is, today, smaller than it has ever been. There is no good reason not to begin.

---

*Veronica S. Dawkins is the founder of the LedgerProof Foundation and of LedgerProof, Inc.*

— end —

> **FOUNDER ACTION REQUIRED:**
> 1. Final polish for your specific voice — this is in your register but is not yet *your* prose.
> 2. Pamela's WSJ editor introduction. Aim for placement July 1.
> 3. If WSJ declines, FT is the immediate next call (same Pamela network). NYT is third.
> 4. Op-ed publication date — anchor a snapshot of the published version on Bitcoin when it goes live.
