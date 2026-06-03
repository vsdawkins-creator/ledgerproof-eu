# IETF SCITT WG mailing list contribution

**To**: `scitt@ietf.org`
**From**: Veronica S. Dawkins <veronica@ledgerproofhq.io>
**Date**: Wed Jun 3, 2026
**Subject**: New publication: OCPP-AI v1.0 specification + W3C VC 2.0 context for draft-dawkins-scitt-ai-article50-00 — eIDAS 2.0 + EBSI alignment for AI Act Article 50

---

SCITT WG —

I am posting today's publication of work that extends draft-dawkins-scitt-ai-article50-00 with concrete deliverables for the EU AI Act Article 50 transparency receipt profile. Three artifacts ship with this note, all under CC BY 4.0 specification license and Apache 2.0 implementations:

(1) The OCPP-AI v1.0 specification (Open Cryptographic Provenance Protocol for AI System Outputs), published at:
    https://spec.ledgerproofhq.io/ocpp-ai-v1.html

   This is the core specification, structured in EU legislative style (Recitals + Articles + Annexes) for the explicit purpose of being citable by the European Commission AI Office and the European AI Board during the Article 50 Guidelines drafting cycle. The technical core remains the SCITT profile defined in draft-dawkins-scitt-ai-article50-00. The legislative styling is an outer presentation layer; the underlying SCITT statement content types are unchanged.

(2) The Anchor Interface Specification v1.0, published at:
    https://spec.ledgerproofhq.io/anchor-interface-v1.html

   This is the substrate-agnostic anchor specification. It defines eight properties (I-1 through I-8) that any conforming anchor substrate must satisfy: immutability under adversarial conditions, public verifiability without authentication, jurisdictional neutrality, demonstrated operational durability of >=36 months, deterministic resolution of anchor records, bounded anchor payload format, the 36-byte OCPP-AI Anchor Payload Format ("LPR1" || merkle_root_32), and GDPR Article 17 compatibility.

   Two reference implementations of the Anchor Interface are described:

   - Bitcoin OP_RETURN (current reference implementation; satisfies all eight properties; described in companion draft-dawkins-scitt-lpr-00)
   - European Blockchain Services Infrastructure (EBSI; satisfies seven properties, with I-4 operational-durability evaluation continuing)

   The dual reference is deliberate. It signals to EU regulatory readers that the SCITT framework is substrate-neutral and admits EU-sovereign anchor substrates as first-class implementations, without sacrificing the jurisdictional neutrality that the AI Act enforcement framework requires.

(3) The W3C Verifiable Credentials 2.0 JSON-LD context, published at:
    https://spec.ledgerproofhq.io/contexts/lpr-v1.jsonld

   This context maps OCPP-AI receipt content body fields to W3C VC 2.0 credentialSubject properties, enabling SCITT statements per the draft profile to be losslessly wrapped as W3C VC 2.0 Verifiable Credentials. The wrapping pattern enables presentation through eIDAS 2.0 Qualified Trust Service Providers for use cases requiring qualified evidence, without modification of the underlying SCITT receipt format.

**Relationship to existing SCITT WG work**

draft-ietf-scitt-architecture and draft-ietf-scitt-scrapi are the architectural and protocol parents of this profile. OCPP-AI does not depart from the SCITT architecture; it specializes it for the EU AI Act Article 50 sub-obligations and provides the substrate-agnostic anchor interface that the SCITT architecture leaves to profile specifications.

The IETF Internet-Draft (draft-dawkins-scitt-ai-article50-00, expires 25 November 2026) remains the canonical SCITT-WG-track document; the materials published today are companion artifacts intended to facilitate review and adoption by EU institutions and Member State competent authorities during the Article 50 Guidelines drafting cycle.

**Specific questions for the WG**

(a) The 36-byte OCPP-AI Anchor Payload Format is presented as substrate-format-neutral; some substrates (notably EBSI smart contract storage) accept payloads of larger size. Should the profile permit substrate-specific payload formats where the substrate accepts larger fields, on the condition that the canonical 36-byte format remains the verifier-resolvable interchange representation?

(b) The dual-anchor publication pattern (Section 5 of the Anchor Interface specification) presumes that verifiers may choose which substrate to accept evidence from. The SCITT architecture does not explicitly address verifier-policy expression. Should the SCITT scrapi specification be extended to admit verifier policy expressions over which substrates a verifier will accept?

(c) The eIDAS 2.0 wrapping pattern (Article 7 of OCPP-AI v1.0) presumes that a Qualified Trust Service Provider can attach an eIDAS Qualified Electronic Signature to a SCITT statement at the VC 2.0 wrapping layer without modification of the SCITT signature. I would welcome WG review of whether this composition pattern requires a normative reference in the SCITT architecture or whether it should remain documented at the profile layer only.

**arXiv preprint**

A unified preprint describing OCPP-AI v1.0, the Anchor Interface, and the eIDAS 2.0 + W3C VC 2.0 compatibility pattern is submitted to arXiv tonight (3 June 2026) under primary classification cs.CR. Expected arXiv ID will be posted to this list within 48 hours of acceptance.

**Reference implementation availability**

Reference implementations are at github.com/ledgerproof (migrating from github.com/vsdawkins-creator/ledgerproof-eu) under Apache License 2.0. Twenty-nine framework adapters covering the principal AI orchestration ecosystems are published.

I will be available at IETF 116 in person for discussion of the profile and welcome WG review of the artifacts published today.

Thanks,

Veronica S. Dawkins
LedgerProof Foundation (in formation)
veronica@ledgerproofhq.io
IETF Datatracker: https://datatracker.ietf.org/doc/draft-dawkins-scitt-ai-article50/

---

## Operator notes (NOT in sent email)

### Send timing
Post tonight after arXiv preprint submission completes. This way the post can reference "arXiv submission completed; expected ID within 48 hours" rather than "in preparation."

### Why this exact framing
- Posts to scitt@ietf.org are public-archived and Google-indexed; this becomes the citation reference for any subsequent AI Office or EAIB review.
- Three specific questions back to the WG create reciprocity — we are contributing to ongoing technical conversation, not just announcing our work.
- The IETF 116 in-person availability signals serious institutional engagement vs. drive-by drop.
- The EBSI inclusion is foregrounded specifically for the EU readers who will eventually parse this archive (DG-CNECT and EAIB analysts use Google Site Search on the IETF archives for context-building).

### Subscription required
The scitt@ietf.org list is open to subscribers. V will need to ensure her IETF mailing list subscription is current under veronica@ledgerproofhq.io before sending; the alternative is to send from her separately-subscribed personal address with the Foundation email in signature. Confirm subscription state before send.

### Cross-post targets after SCITT
After the SCITT post lands, consider cross-posting (with explicit attribution to the original SCITT thread to avoid spam concerns):

- W3C VC WG mailing list (public-vc-wg@w3.org) — focused on the JSON-LD context contribution
- CEN-CENELEC JTC 21 national mirror committee (via DIN-SME membership once filed)
- AI Standards working group at ENISA (ENISA AISC) — focused on the cryptographic provenance angle

### What this does NOT do
This post is technical contribution, not regulatory advocacy. It does not lobby for citation, does not name specific Commission officials, does not make political claims about the Brussels Effect. The political framing lives in the OCPP-AI v1.0 Recitals (which the post links to but does not quote). This separation preserves SCITT WG list etiquette while still making the political framing publicly readable for any EU reviewer who follows the link.
