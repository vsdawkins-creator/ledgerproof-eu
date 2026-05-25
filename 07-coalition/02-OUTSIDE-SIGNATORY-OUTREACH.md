# Outside Signatory Outreach — Three Asks

> Each of the three outside signatory asks below. Cold-warm: a board member or advisor opens the door; the founder follows up. Each ask is small (sign one Manifesto, optionally one quote in the press kit). No board seat involved.

---

## Ask 1 — Peter Todd (Bitcoin / OpenTimestamps)

**Opened by:** Frank Gale (cold; Frank has Bitcoin-world introductions) OR direct from Veronica via established public-channel etiquette.
**Channel:** Email or Twitter DM, then GitHub if engagement.

### Subject: LedgerProof — OpenTimestamps-superset profile, would value 30 min before publication

Peter —

Veronica Dawkins, founder of LedgerProof. I am writing because the work I am about to publish builds directly on what you built ten years ago, and I would rather hear your objection now than read it after launch.

LedgerProof Receipt v1.0 (LPR) is an open Bitcoin-anchored receipt format that extends the OpenTimestamps timestamping construction with three additions: an Ed25519 authorship-signing field, a CBOR-canonical structured-data wrapper, and a chain-linkage convention for receipts in an authorial sequence. The OPR (OTS-Profile-Receipt) sub-profile of LPR is a strict subset of LPR; any LPR receipt with the additional fields omitted degrades cleanly into an OpenTimestamps proof verifiable by the existing OTS toolchain. We anchor on Bitcoin via the same OP_RETURN aggregation pattern OpenTimestamps uses, with a distinguishing 4-byte prefix (`LPR1`) so an OTS calendar and an LPR calendar do not collide.

The reason for the additional fields is the EU AI Act Article 50 enforcement on August 2: the regulators need authorship signing and structured authorial chaining; OpenTimestamps was not built to carry those, and I did not want to bolt them onto OpenTimestamps without your knowledge. So I built a profile that composes alongside OpenTimestamps rather than diverging from it.

Three things I would value from you, in whatever order is convenient:

1. **A technical look** at the LPR 1.0 specification (attached / `ledgerproofhq.io/lpr-1.0-spec`) and the reference implementation, with whatever objections, corrections, or "this is wrong, here is why" you have. I will incorporate before publication on July 6 if I have time and the change is mine to make.
2. **A response to the OPR sub-profile design choice.** I want OPR proofs to be verifiable by an unmodified OTS verifier. If the OPR construction does not in fact achieve that, I want to fix it.
3. **An optional signature on the Provenance Manifesto** that accompanies the launch. The Manifesto is a one-page statement about the integrity of the documentary record in the AI era. Other signatories include Pamela Jefferson (Columbia Journalism), Chris Morton (JPMorgan), Frank Gale (Riot), and a handful of additional outside signatories. Your name would matter to the cryptographic community in a way no other signature could. **No obligation.** If you read the Manifesto and prefer not to sign, the LPR work proceeds regardless and your technical review remains, separately, the highest-leverage feedback we could receive.

Happy to take this to any channel you prefer — Twitter DM, GitHub issue, the OpenTimestamps mailing list, a video call, a written response in your own time.

Thank you for the work.

— Veronica S. Dawkins
LedgerProof Foundation (in formation)
[email] · [Bitcoin address for verification of this email's authorship]

> **FOUNDER ACTION REQUIRED:** This ask should be sent only after you have published the LPR spec to GitHub (the link in the email needs to resolve to a real public spec, not a private draft). The "Bitcoin address for verification" line is optional but on-brand. Frank can warm-introduce if he has Bitcoin-community contacts; otherwise this is a cold email to Peter's published address — which is the right etiquette and will not be held against you.

---

## Ask 2 — Article-50-exposed European enterprise (a media or publishing org)

**Opened by:** Pamela Jefferson via Columbia J-School alumni network — target organizations: Reuters, the Guardian Media Group, Le Monde, Der Spiegel, Süddeutsche Zeitung, the BBC, the European Broadcasting Union, the World Editors Forum.
**Channel:** Warm intro to a named individual at the C-level or General Counsel level.

### Subject: 25 days to Article 50 — invitation to be a named founding signatory of an open response

[Recipient name] —

I am writing on the warm introduction of [Pamela Jefferson / Columbia J-School]. I am the founder of the **LedgerProof Foundation**, a nonprofit corporation publishing an open, vendor-neutral cryptographic-provenance standard for documents and AI-generated content, anchored on the Bitcoin blockchain. Our public launch is July 6, 2026 — twenty-five days before EU AI Act Article 50 enforces.

I would like to invite [Organization] to be a **founding signatory** of the **Provenance Manifesto** we are publishing on July 6.

What this means in practice:

- A one-page declaration about the integrity of the documentary record in the AI era. The Manifesto is the cultural artifact of the launch; the LPR 1.0 cryptographic specification is the technical one. The two are anchored together on Bitcoin at the launch.
- Your organization's name in the signatory list, alongside the Foundation's board members and a small number of additional founding signatories from the cryptographic community, journalism, and academia.
- No commercial commitment, no contractual obligation, no recommendation that your organization adopt LPR. You are signing the Manifesto, not the spec.

Why this matters to your organization, in plain terms:

- Article 50 enforcement on August 2 will produce a press cycle in which the question *how is your newsroom marking AI-generated content* will be asked of every major European publisher. Being a signatory to a public statement about what the documentary record requires — independent of any commercial dependency — is an asset in that cycle.
- The Manifesto explicitly does not advocate for one technology. It states the condition of the documentary economy and the principle that any technical response must be open, public, free at the point of verification, and not dependent on any single vendor.
- Signatures are public. The Manifesto's verification path is public. Your countersignature is itself anchored on Bitcoin.

I would value 30 minutes on Zoom in the next ten days to discuss. If your organization's policy precludes signing public manifestos of this kind, I understand — please tell me and we will instead invite you to be among the first organizations the Foundation briefs after launch, with the same materials, in advance of any institutional decision your organization may face.

With respect,

Veronica S. Dawkins
LedgerProof Foundation (in formation)

> **FOUNDER ACTION REQUIRED:** Pamela identifies the right named individual at one (and ideally two backup) outlets. Goal: one signature by Day 17. Pamela makes the warm intro; Veronica sends this email under it.

---

## Ask 3 — AI-ethics academic (a credentialed voice)

**Opened by:** Pamela Jefferson via the Columbia academic network OR cold via published research-group contact.
**Target candidates:** A faculty member at the Stanford HAI institute, MIT Schwarzman College of Computing, Oxford Internet Institute, AI Now Institute (NYU), Berkman Klein Center (Harvard), or the AI Safety Institute community. Prefer a tenured or senior researcher with cross-domain credibility (law-and-AI, policy-and-AI, or cryptography-and-AI).

### Subject: LedgerProof Foundation — invitation to be a founding signatory of the Provenance Manifesto

Professor [Name] —

[Warm intro language from Pamela / referrer goes here.]

I am the founder of the LedgerProof Foundation, a nonprofit corporation publishing an open, Bitcoin-anchored cryptographic-provenance standard for documents and AI-generated content. Our public launch is July 6, 2026, twenty-five days before EU AI Act Article 50 enforces.

I am writing to invite you, in your personal academic capacity, to be a founding signatory of the **Provenance Manifesto** the Foundation is publishing on July 6. The Manifesto is a one-page declaration about the integrity of the documentary record in the AI era — not an endorsement of one technology, not a commercial recommendation, not a position your institution must adopt. It states a condition and a principle: that the integrity of the documentary record now requires open public infrastructure, free at the point of verification, durable beyond the survival of any single vendor.

What I would ask:

- A look at the Manifesto (1 page, attached) and the Founding Whitepaper (9 pages, also attached) at your pace, in the next 14 days.
- If the content is something you can sign in your personal academic capacity (most universities permit personal signatures on public letters of this kind, with a footnote that institutional affiliation is for identification only), your countersigned signature in the document.
- No board role, no commercial relationship, no commitment beyond the signature itself.

Why I am writing to you specifically: the credibility of an open cryptographic-provenance standard at the moment of Article 50 enforcement will depend, in part, on whether the public statements about it carry the names of researchers whose institutional independence is beyond question. Your work in [specific area] has shaped how a generation of policymakers think about [specific topic]; I would be honored to have your judgment associated with this work, and I would be more than satisfied if your judgment, after reading, is that the Manifesto is not something you wish to sign.

Available for a 30-minute call if useful. Written response equally welcome.

With respect,

Veronica S. Dawkins
LedgerProof Foundation (in formation)

> **FOUNDER ACTION REQUIRED:** Pamela identifies 3-5 target academics. Two warm intros placed by Day 10. One signature confirmed by Day 21. If none of the academic asks lands, the Manifesto launches with the institutional signatories alone — the academic name is desirable, not required.
