# Futurium Post 01 — LedgerProof: an open cryptographic protocol for Article 50 transparency evidence

**Drafted**: Tuesday June 2, 2026
**Author voice**: LedgerProof Foundation (institutional, not founder-personal)
**Audience**: European AI Alliance forum readers — Commission staff (DG-CNECT, EU AI Office), national competent authority delegates (BaFin, CNIL, BfDI, AGCOM, AP, AESIA), CEN-CENELEC JTC 21 members, academic researchers, SME representatives via DIGITAL SME Alliance, AI policy NGOs, member-state permanent representations
**Platform**: https://futurium.ec.europa.eu/en
**Status**: Draft for Veronica's review before posting
**Length**: ~1,250 words

---

## Suggested title

**An open cryptographic protocol for EU AI Act Article 50 transparency evidence — a first post, and an invitation**

## Suggested subtitle / lead paragraph (Futurium-visible)

The LedgerProof Foundation is publishing here because the work we are building needs scrutiny from this community before August 2 enforcement begins, and because the open-protocol approach to Article 50 evidence we have chosen is only useful if it genuinely serves deployers, regulators, and SMEs across the Union. This first post explains what the protocol is, what it does, what it does not do, and what we would value from this forum.

---

## Body

### What Article 50 actually asks for

Article 50 of the AI Act (Regulation (EU) 2024/1689) obliges providers and deployers of certain AI systems to ensure that natural persons are informed, in clear and distinguishable form, when they are interacting with an AI system, when content has been generated or manipulated by an AI system, and when emotion recognition or biometric categorisation is being used. Enforcement begins on Tuesday August 2, 2026.

The substantive obligation is real and uncontroversial. The implementation question is less settled: in what evidentiary form should compliance with Article 50 be demonstrated to a competent authority on request? Today, the most common answer across early deployments is one of three things: structured logging written to a cloud provider's storage (Amazon CloudWatch, Azure Monitor, Google Cloud Logging), a vendor-supplied compliance PDF that asserts conformity without external verifiability, or a process-based attestation contained in the deployer's internal documentation. None of these answers is straightforwardly verifiable by a supervisory authority without granting that authority access to the deployer's internal systems and to the vendor's representations. None of them survives the cryptographic auditability bar that ordinary financial-services supervisory regimes have come to expect for analogous obligations.

### What LedgerProof is

LedgerProof is an open cryptographic protocol that produces a small, verifiable record — a *receipt* — for each AI-touched interaction within scope of Article 50. A receipt is a deterministic, canonically-encoded record of a small set of fields: the model identifier, the prompt hash, the response hash, the timestamp, the deployer identifier, the regulatory context, and a small number of additional fields where applicable. The receipt is signed by the deployer using an Ed25519 signature over the canonical bytes. Receipts produced within a configurable time window — by default sixty minutes, configurable down to ten minutes for high-volume deployers — are aggregated into a Merkle tree. The root of that tree is anchored to the Bitcoin mainnet via a thirty-six-byte OP_RETURN payload of the form `LPR1 || merkle_root_32`. Once anchored, the existence and integrity of any receipt within the tree is independently verifiable against the public Bitcoin chain.

The protocol design is published as an IETF SCITT-track Internet-Draft (`draft-dawkins-scitt-ai-article50-00`) currently on the IETF Datatracker. Reference implementations exist in Rust, Python, and TypeScript and are published under the Apache 2.0 licence. The reference verifier is a single-file static HTML page that runs in any modern browser, requires no installation, and performs all verification client-side.

### The load-bearing property the protocol exists to protect

A receipt issued by any deployer using LedgerProof can be independently verified by any party — the deployer themselves, the deployer's external auditor, a supervisory authority, an academic researcher, or any interested natural person — using exactly three inputs: a copy of the Bitcoin chain (publicly available, fits on commodity hardware), the published protocol public key (published in the IETF draft and at the Foundation's transparency page), and the receipt itself. No call to LedgerProof Foundation infrastructure is required. No call to any single operator's infrastructure is required. No paid subscription is required. No data leaves the verifying party's machine.

This property is the design condition for credible regulatory positioning under Article 50, and it is the property the Foundation exists to protect. If the LedgerProof Foundation ceases to exist tomorrow, every receipt ever issued under this protocol remains verifiable against the public Bitcoin chain indefinitely.

### What this protocol is *not*

We are being explicit about boundaries because regulatory-anxious legal teams ask, and because the open-standards community is rightly suspicious of vendors who blur these lines:

- **The protocol is not endorsed** by the European Commission, the EU AI Office, EBA, EIOPA, ESMA, or any national competent authority. Endorsement is not something a regulator does for a vendor's protocol, and we do not seek it. What regulators receive is published technical documentation and Foundation submissions to consultations, on Foundation letterhead, asking for protocol-approach feedback.

- **The protocol does not confer presumption of conformity** under Article 40 of the AI Act. Presumption of conformity flows through harmonised European standards published in the Official Journal under standardisation request M/593. The LedgerProof Foundation participates in that process via DIN SME membership and the CEN-CENELEC JTC 21 working group — but presumption of conformity is a separate question that runs through a separate institutional process, and our Founding Member agreements explicitly do not promise it.

- **The protocol is not exclusive**. The Foundation's IP licence is perpetual, royalty-free, irrevocable, and non-exclusive. LedgerProof Inc. — the commercial entity that ships hosted operator services and the reference SDKs — is one implementer of the protocol. Any third party, including a competitor of LedgerProof Inc., may implement the protocol under the same terms.

- **The protocol does not create vendor lock-in**. Receipts produced via any operator's service remain verifiable using the public protocol stack indefinitely, regardless of whether a deployer continues to use that operator, migrates to another, or runs their own anchoring infrastructure.

### Where the work stands today

- **IETF SCITT-track**: `draft-dawkins-scitt-ai-article50-00` published on Datatracker. Working group adoption in progress.
- **CEN-CENELEC JTC 21**: DIN SME membership application in preparation, target filing this month. New Work Item Proposal under development.
- **ISO/IEC JTC 1/SC 42**: mirror activities aligned with JTC 21.
- **ETSI ISG-SAI**: observer status in development.
- **Code of Practice for GPAI (transparency chapter)**: Foundation consultation submission targeted for end-of-June filing.
- **Independent cryptographic audit**: engagements with established review firms are being scheduled for publication later in the summer. The combined audit memo will be published openly under the Foundation's transparency commitments.
- **Reference implementations**: Rust, Python, and TypeScript SDKs and the reference verifier are open-source under Apache 2.0 at the Foundation's public repository.

The Foundation itself is organised as a multi-jurisdictional structure: a United States 501(c)(3) public charity (Delaware, in formation) with a Dutch Stichting EU subsidiary (Amsterdam, in formation) serving as the European contractual counterparty. Foundation governance documents (Conflict of Interest Policy, IP Transaction Committee Charter, Foundation Advisory Council Charter) are published as anchored public receipts on adoption. An independent Board of three directors, none of whom hold equity in LedgerProof Inc., will be confirmed by the end of August.

### What we would value from this community

Three specific kinds of input would be substantively useful:

1. **From SME representatives**: Does the open-protocol-with-zero-ongoing-cost approach actually meet the SME-friendliness bar Article 50 implementation requires? Are there structural blind spots — implementation cost, technical complexity, dependency assumptions — that disadvantage smaller deployers in ways we have not anticipated?

2. **From supervisory authority delegates**: Does the offline-verifiability property meaningfully reduce the supervisory burden of Article 50 enforcement, or does it shift the burden in ways that create new problems? What additional fields or properties would your competent authority need for a receipt to be substantively useful in an enforcement action?

3. **From standards-body and Commission readers**: Is the IETF SCITT + CEN-CENELEC JTC 21 institutional path the appropriate venue for this work to mature, or are there other tracks (ETSI, ISO/IEC SC 42, sector-specific harmonisation) that would be more productive to engage in parallel?

We are publishing here as the first of a series of Foundation posts that will document the protocol's evolution, the consultation submissions we make, and the independent audit results as they publish. Subsequent posts will go deeper on specific properties (GDPR Article 17 erasure compatibility, OP_RETURN persistence characteristics, the canonical-encoding cross-language conformance regime, and the slug-router authorisation surface).

The protocol is open. The Foundation is open. The work is improved by scrutiny. We are grateful for the time of anyone in this community who chooses to engage substantively, and we will respond to feedback in public on this thread.

---

**LedgerProof Foundation**
*In formation. United States 501(c)(3) public charity (Delaware) with Dutch Stichting EU subsidiary (Amsterdam).*
- IETF draft: `https://datatracker.ietf.org/doc/draft-dawkins-scitt-ai-article50/`
- Foundation transparency page: `https://ledgerproofhq.io/foundation`
- Open code: `https://github.com/ledgerproof`
- Foundation contact: `foundation@ledgerproof.org`

---

## Pre-post review checklist for Veronica

Before posting to Futurium, please verify:

- [ ] **Voice** — institutional, no first-person founder phrasing, no marketing language. Reads as Foundation publication.
- [ ] **C1 discipline** — the "what this is not" section explicitly disclaims regulator endorsement and Article 40 presumption of conformity. Nothing elsewhere in the post implies otherwise.
- [ ] **C4 discipline** — local verifiability is named explicitly. No phrasing suggests SaaS-dependency.
- [ ] **No specific customer names** — Klarna, Adyen, ING, Wise, Allianz, Riot, Mistral all absent. Correct for this audience.
- [ ] **No financial details** — no seed close, no Founding Member tier prices, no operating model numbers. Correct for this audience.
- [ ] **Standards-body names accurate** — DIN, CEN-CENELEC JTC 21, ISO/IEC JTC 1/SC 42, ETSI ISG-SAI, IETF SCITT WG — all spelled and characterised correctly.
- [ ] **Regulation references accurate** — Regulation (EU) 2024/1689 (the AI Act), Article 40 (presumption of conformity via harmonised standards), Article 50 (transparency obligations), standardisation request M/593 — all spelled and characterised correctly.
- [ ] **Three-input verification claim accurate** — Bitcoin chain + published protocol public key + receipt — matches the actual SDK and reference verifier behaviour.
- [ ] **IETF draft URL works** — confirmed live on Datatracker.
- [ ] **No promises of timing we can't keep** — "audit engagements scheduled for publication later in the summer" is appropriately vague; do not name a specific date.
- [ ] **No promises of governance we haven't delivered** — Foundation Board "confirmed by end of August" matches `WC-05` in `win-conditions.json`. Adjust if WC-05 has moved.

## Posting mechanics on Futurium

When you log into futurium.ec.europa.eu:

1. Confirm your Foundation profile is set up (Foundation name, role, jurisdiction). Reach out to me before clicking Save if any field is unclear — Foundation jurisdiction labelling should match our `/foundation` page exactly.
2. Find the **European AI Alliance** group / forum (the most appropriate sub-forum is typically "AI Alliance Discussions" or the closest active thread on the AI Act / Article 50 implementation).
3. New post → paste this body. The platform supports basic Markdown; if formatting renders poorly, plain paragraphs work fine.
4. Tag the post with the most relevant tags (typically: "EU AI Act," "Article 50," "transparency obligations," "standards," "open source" — choose what's actually available).
5. Do NOT include the pre-post review checklist or this "Posting mechanics" section. Post body only — from the suggested title through the Foundation contact block.

## What happens after post

The post is the first public artefact tying the Foundation to the EU AI Alliance ecosystem. Specific anticipated effects:

- Hallensleben, Toffaletti, Birkholz, and other Foundation real-10 contacts may see the post organically on the platform. This warms subsequent outreach without requiring cold introduction.
- Commission desk officers monitoring Futurium for stakeholder input on Article 50 implementation may flag the post into their Code of Practice consultation files.
- SME representatives may engage in the thread, which generates substantive feedback we can fold into the protocol or into the DIN NWIP.
- The Foundation should respond to substantive comments in public, on the thread, with the same institutional voice. First responses ideally within 24 hours of an inbound comment.
- Anchor a record of this post as a Foundation receipt (post URL + post text + post date) once it is live — this is a Foundation publication and belongs in the transparency-receipts series.

If you want, after the post is live I can draft template responses for the three most likely categories of comment (SME implementation concern / regulator scope question / standards-body process question) so you have prepared institutional responses ready within the first 24-hour window.
