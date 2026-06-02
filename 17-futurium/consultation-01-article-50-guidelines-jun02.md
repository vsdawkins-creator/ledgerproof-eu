# Stakeholder consultation submission — Draft Guidelines on the implementation of the transparency obligations for certain AI systems under Article 50 of Regulation (EU) 2024/1689

**Submitted to:** European Commission, DG-CNECT, Artificial Intelligence Office — AI Regulation and Compliance Unit
**Consultation:** Draft Guidelines for stakeholder consultation on Article 50 AI Act
**Submission platform:** Futurium (European AI Alliance)
**Submission date:** 2 June 2026
**Submitting organisation:** LedgerProof Foundation
**Organisational form:** United States 501(c)(3) public charity (Delaware, in formation) with Dutch Stichting EU subsidiary (Amsterdam, in formation, under counsel of NautaDutilh)
**On whose behalf:** The LedgerProof Foundation (the organisation itself)
**Primary sector of activity:** Information technology
**Additional sectors of activity:** Banking and finances; Consumer protection; Cultural and creative sector including media; Healthcare; Legal services sector
**Sections of the draft Guidelines addressed:** Section II (contextual), Section III, Section IV, Section VI, Section VII

---

## Activities description (intended for the form's 1,300-character field)

The LedgerProof Foundation is a public-interest, in-formation US 501(c)(3) public charity, with a Dutch Stichting subsidiary serving as the European contractual counterparty. The Foundation stewards the LedgerProof Protocol, an open, royalty-free cryptographic protocol that produces independently verifiable receipts for AI-deployment governance events within the scope of Article 50 of Regulation (EU) 2024/1689. Reference implementations are published under the Apache 2.0 licence. The protocol is on the IETF SCITT track as Internet-Draft `draft-dawkins-scitt-ai-article50-00`. The Foundation engages standards processes in parallel through CEN-CENELEC JTC 21 (via DIN SME membership in preparation) and ISO/IEC JTC 1/SC 42 mirror activities. The Foundation makes no claim of Commission endorsement and does not seek inclusion in any regulator-published reference list. This submission is offered as a public-interest contribution to the consultation record.

---

## Preamble — purpose and discipline of this submission

The Foundation respectfully offers the following technical observations on the draft Guidelines. The submission is structured to assist the Commission's drafting team by giving paragraph-specific commentary rather than general advocacy. The Foundation makes three specific requests of the Commission, set out at the end of this submission. The Foundation does not seek, and explicitly does not request, vendor inclusion in any list, reference catalogue, or recommended-implementation registry. The contribution we offer is to the public regulatory record on the question of how Article 50 obligations may be evidenced — not whether a particular protocol should be preferred.

We have organised the substantive commentary around four of the Guidelines' Sections in which we believe the Foundation has standing to contribute: Section III (Article 50(1)), Section IV (Article 50(2)), Section VI (Article 50(4)), and Section VII (Article 50(5)). We open with brief contextual observations on Section II in order to frame the discussion.

The Foundation acknowledges the disclaimer at the head of the draft Guidelines: that the text is a draft working document, that it does not prejudge the final decision of the Commission, and that authoritative interpretation of the AI Act ultimately rests with the Court of Justice of the European Union. Nothing in this submission should be read as proposing otherwise.

---

## Section II — Overview of transparency obligations and horizontal topics (contextual observations)

### On §2.3 — Responsible actors under Article 50 AI Act

The draft Guidelines at §2.3 set out a coherent allocation of responsibility as between providers (Article 3(3) AI Act) and deployers (Article 3(4)), and clarify at points (12) to (14) that disseminating actors and other value-chain participants are encouraged to preserve marks and labels even where they fall outside the Article 50 obligation perimeter.

The Foundation offers one structural observation. The clarification at point (14) — that safeguarding trust and integrity of the information ecosystem is a shared responsibility — is correct, and the encouragement to value-chain actors is welcome. The Guidelines do not, however, contemplate the circumstance in which a deployer wishes to provide an external party (an auditor, a competent authority, a downstream platform applying its own preservation policy under §4.4) with evidence that a particular interaction or content item was in fact handled in conformity with Article 50. Today, the practical answer in most deployments is one of three: structured logs written to the deployer's own infrastructure, a vendor-supplied attestation contained in a compliance PDF, or an internal process record. None of those answers is independently verifiable by an external party without granting access to the deployer's systems.

This is not a defect of the Guidelines as drafted. It is, however, an evidentiary gap with consequences for several specific obligations addressed in later Sections. We return to this in the commentary on §§3.1.2, 4.2.1–4.2.3, 6.2.3, and Section VII.

### On §2.4.3 — AI systems released under free and open-source licences

The draft Guidelines at §2.4.3 correctly clarify that the open-source exclusion in Article 2(12) AI Act does not exempt providers and deployers from the transparency obligations of Article 50. The Foundation supports this clarification without reservation. We observe only that an open-protocol approach to evidencing those obligations — meaning a protocol whose specification is publicly available under a permissive licence, whose reference implementations are open-source, and whose verification can be performed independently of any vendor's infrastructure — sits comfortably within the policy direction signalled at this point. The open-source exclusion concerns the AI system itself; the compliance toolchain can be open even where the system is proprietary, and an open compliance toolchain reduces the supervisory burden on competent authorities asked to verify compliance across heterogeneous deployments.

---

## Section III — Article 50(1) AI Act: Transparency for Interactive AI Systems

This Section is the Foundation's principal area of substantive commentary.

### On §3.1.2 — Information obligation under Article 50(1) AI Act, paragraphs (29) to (37)

**On paragraph (30) — lifecycle responsibility of providers.** The draft Guidelines correctly state that providers are responsible for ensuring natural persons are effectively informed throughout the lifecycle of the AI system, including after placement on the market and putting into service. The Foundation observes that this lifecycle obligation, properly understood, requires the provider to retain some form of demonstrable evidence that the information mechanism was operative at relevant moments in the system's lifecycle. The Guidelines do not, at this point, address what form that demonstrable evidence should take. Design-time documentation (specifications, screenshots, terms of service) demonstrates that a mechanism was *designed*; it does not demonstrate that the mechanism was *operative* with respect to any particular natural person at the time of first interaction.

This is the evidentiary distinction the Foundation respectfully invites the Commission to make more explicit. A provider seeking to demonstrate compliance to a market surveillance authority under §8.2 should be able to produce evidence not only of design-time intent, but of run-time conformity. Such evidence may take several forms, including: server-side logs, telemetry retained by the provider, screenshots of the deployed user interface, and — relevant to the Foundation's contribution — externally verifiable, cryptographically signed records of the disclosure event itself.

**On paragraph (33), final clause — AI identifiers or credentials disclosed in a verifiable manner.** The draft Guidelines already contemplate "AI identifiers or credentials (e.g. AI agents that disclose their AI identity, including as appropriate in a verifiable manner)." The accompanying footnote (20) refers to electronic attestations of attributes established under Regulation (EU) No 910/2014 and made available through the EU Digital Identity Wallets and the proposed European Business Wallets. The Foundation supports this direction and observes that the verifiability principle articulated in paragraph (33) extends naturally beyond identity attestation to disclosure-event attestation. The same standards-aligned reasoning that permits an AI agent to disclose its identity in a verifiable manner also permits a provider to produce a verifiable record that the disclosure occurred.

The Foundation respectfully suggests that paragraph (33) could be strengthened by an additional clause along the following lines (proposed for the Commission's consideration, not as a redline):

> *In addition to verifiable disclosure of the AI agent's identity, providers may produce externally verifiable, cryptographically signed records that the disclosure required under Article 50(1) was provided to the natural person at the relevant moment. Such records may form part of the evidence on which the provider relies to demonstrate compliance to competent authorities. The use of any particular technique for producing such records is at the provider's discretion and is not prescribed by these Guidelines.*

The Foundation is not asking the Commission to prescribe any particular implementation. The Foundation is asking the Commission to recognise that externally verifiable evidence is a category of compliance mechanism, distinct from design-time documentation and from internal logs, that should be available to providers who choose to use it.

**On paragraph (35) — techniques considered insufficient when used alone.** The draft Guidelines correctly observe that disclosures contained only in terms and conditions, machine-readable markings invisible to the user, ambiguous signals, and capability-only descriptions are not by themselves sufficient to fulfil the Article 50(1) obligation. The Foundation supports each of these clarifications.

We note that the second bullet — that machine-readable markings (e.g. metadata or watermarks) which are not perceivable by users at the point of interaction cannot, *alone*, fulfil the transparency obligation in Article 50(1) — is correct and important. We invite the Commission to consider, however, that this correct statement should not be read as a discouragement to providers from *also* producing machine-readable records of the user-facing disclosure event. The user-facing disclosure satisfies the information obligation; the machine-readable record provides the evidence of compliance. These are complementary, not alternative.

**On paragraph (37) — context-aware disclosure in sustained or evolving interactions.** The Guidelines correctly observe that one-time disclosures at the beginning of an interaction may be inadequate in sensitive contexts. The Foundation observes that any such requirement for repeated, context-aware disclosure increases the evidentiary load on providers. A provider who is obliged to demonstrate that a periodic reminder was delivered to a vulnerable natural person at a particular moment will require, in practice, some form of contemporaneous record. The Foundation respectfully suggests that the Guidelines could usefully acknowledge the evidentiary dimension of the obligation that paragraph (37) imposes.

### On §3.2.1 — Exception for obvious interaction with an AI system, paragraphs (39) to (42)

The "obvious interaction" exception is, as the Guidelines correctly observe, drawn from established EU consumer-protection law and rests on a hypothetical reasonably well-informed, observant and circumspect average natural person within the target audience.

The Foundation observes an asymmetric evidentiary gap inherent to this exception. A provider claiming the benefit of the exception is, in effect, asserting that no disclosure was required because the artificial nature of the interaction was obvious. A natural person disputing the application of the exception — for instance, a vulnerable user who claims they did not perceive the interaction as artificial — is in a structurally weaker position. Today, the dispute is adjudicated on the basis of design-time documentation, marketing materials, and post-hoc reconstruction.

The Foundation respectfully suggests that the Guidelines could helpfully address the evidentiary posture of the obvious-interaction exception. One possibility — offered for the Commission's consideration — is to clarify at paragraph (42) that providers relying on the exception should retain evidence sufficient to demonstrate, with respect to any particular interaction the subject of a dispute, the contextual factors on which the obviousness assessment relied at the time of interaction. The form such evidence takes is at the provider's discretion. The principle — that the burden of demonstrating obviousness rests with the party invoking the exception — is one the Guidelines could productively make explicit.

### On §3.3 — Interplay with other Union legal acts, paragraphs (47) to (49)

The draft Guidelines correctly state at paragraph (49) that Article 50(1) fulfils a different objective from the information obligations to data subjects under EU data protection law. The Foundation supports this distinction.

The Foundation observes one practical interaction worth surfacing. Article 13 and 14 GDPR require controllers to provide information about processing at the point of collection (Article 13) or within a reasonable period after obtaining the data (Article 14). Where an AI system within scope of Article 50(1) processes personal data, the controller's GDPR information obligation and the provider's Article 50(1) information obligation can frequently be discharged by overlapping or co-located disclosures, while remaining doctrinally distinct. Where a provider chooses to evidence compliance with both obligations through a single coherent disclosure record, that practice should not be discouraged. The Foundation respectfully suggests that paragraph (49) could be supplemented by a clarification that combined evidence covering both Article 50(1) and the corresponding GDPR information obligations is permissible, provided both substantive obligations are independently satisfied.

The forthcoming joint Commission and EDPB guidelines on the interplay between the AI Act and EU data protection law (referenced at footnote 24) would be the more natural home for this clarification; we flag it here for cross-referencing.

---

## Section IV — Article 50(2) AI Act: Marking and Detection of AI-generated or manipulated content

### On §4.2.1 — The marking element, paragraphs (67) to (70)

**On paragraph (69) — examples of marking techniques.** The draft Guidelines, citing Recital 133 AI Act, identify a non-exhaustive list of marking techniques: watermarks, metadata identifications, cryptographic methods for proving provenance and authenticity of content, logging methods, fingerprints, or other techniques, and combinations thereof. The Foundation supports the non-exhaustive, technology-neutral character of this list.

We respectfully note that the published literature on in-band watermarking — particularly for text and audio modalities — documents systematic robustness limitations under common alterations (re-encoding, paraphrase, format conversion) and adversarial conditions. The state of the art is moving, and the Commission's commitment to allow combinations of techniques is well-judged. The Foundation observes that out-of-band cryptographic evidence — a signed, anchored record that a particular content item was produced or manipulated by a particular AI system at a particular time — complements in-band marking by providing a verification path that does not depend on the survival of the in-band mark through downstream transformation.

The Guidelines at paragraph (69) note that "such provenance methods may also be used for compliance with Article 50(2) and be conducive in enabling natural persons to distinguish AI-generated or manipulated content." The Foundation welcomes this clarification and respectfully suggests it could be strengthened by an explicit acknowledgement that cryptographic provenance methods may be used in combination with content-level marking to satisfy the requirements of effectiveness, robustness, reliability and interoperability collectively, as contemplated at §4.2.3.

**On paragraph (70) — implementation at different stages of the value chain.** The Foundation supports the clarification that providers may implement marking at the level of the AI system or the underlying AI model, and may rely on open-standard or third-party marking solutions, without prejudice to their own responsibility for compliance. This formulation correctly accommodates open-protocol approaches in which a marking and detection solution is implemented as a public good rather than as a single-vendor offering.

### On §4.2.2 — The detection element, paragraphs (71) to (73)

**On paragraph (72) — detection tools.** The draft Guidelines define a detection tool as "a mechanism that detects whether content has been AI-generated or manipulated, typically identifying technical markers or signatures that verify its origin." This formulation is technology-neutral and the Foundation supports it.

We respectfully observe one important corollary. A detection mechanism that relies on retrieval and verification against a separately maintained registry of content fingerprints or content receipts — a so-called "out-of-band" detection mechanism — falls within the scope of this definition. Such mechanisms can offer detection properties that in-band techniques do not (notably, verifiability against an authoritative external record), at the cost of requiring network access to the registry at the moment of detection. The Guidelines should not, in our respectful view, be read as preferring in-band over out-of-band approaches, or vice versa. Both can satisfy the obligation, and many production deployments will combine them.

The Foundation respectfully suggests that paragraph (72) could be supplemented by a clarification along the following lines (proposed for the Commission's consideration):

> *Detection mechanisms may be implemented in-band, where the verification of artificial origin is performed against the content itself, or out-of-band, where the verification is performed against a separately maintained record corresponding to the content (such as a signed, anchored receipt held in a publicly accessible registry). Both approaches may, alone or in combination, satisfy the requirements of effectiveness, interoperability, robustness and reliability set out in the second sentence of Article 50(2) AI Act.*

### On §4.2.3 — Compliance with the requirements for technical solutions: effective, interoperable, robust and reliable, paragraphs (74) to (82)

**On paragraphs (74) and (75) — the four quality requirements.** The Foundation supports the technology-neutral formulation of the four requirements. The clarification at paragraph (75) that the combination of technical solutions must holistically meet all requirements, and that complementarities and limitations of various solutions should be taken into account, is well-judged. The Foundation respectfully observes that this combinative reading is essential: as paragraph (78) acknowledges, "under the current state-of-the-art there is no single technique for marking and detection that meets all four requirements at the same time to the legally required degree."

**On paragraph (78) — combinative reading.** The Foundation strongly supports the clarification at paragraph (78). We observe that in this combinative landscape, the Guidelines should be read to permit, and to encourage, the pairing of approaches with different strengths: in-band watermarking provides perceptual immediacy and survives offline; out-of-band cryptographic receipts provide independent verifiability and survive adversarial in-band degradation. Neither alone discharges the requirement in full; together they can. We respectfully suggest the Guidelines could productively add an illustrative example in this direction at or near paragraph (78).

**On paragraph (74), interoperability sub-bullet.** Interoperability is, of the four requirements, the one most exposed to single-vendor capture. A provider's marking solution that produces marks readable only by that provider's detection tool would not satisfy the interoperability requirement as defined. The Foundation respectfully suggests that the Guidelines could productively clarify that interoperability requires, at a minimum, the publication of a specification sufficient for an independent third party to implement a conforming detection mechanism. The publication of such a specification under a permissive licence (for example, an Apache 2.0 or Creative Commons by-attribution licence) is one way to satisfy this minimum, but is not the only way; the Foundation does not propose that publication under any particular licence be required.

**On paragraph (76) — technical feasibility.** The Foundation supports the objective formulation of technical feasibility and the clarification that it does not depend on the resources of any individual provider. The clarification that providers are not obliged to use solutions not yet developed or available on the market is correct and protects providers from being held to a standard that does not exist at the time of placement on the market. We observe only that this formulation also implies a positive responsibility on standards-setting bodies, regulators, and the wider technical community to ensure that an adequate state of the art continues to develop. The Foundation is engaged in this development through the IETF SCITT working group and through CEN-CENELEC JTC 21.

### On §4.3 — Exceptions to the obligations under Article 50(2) AI Act, paragraphs (83) to (87)

**On paragraph (84) — assistive function for standard editing.** The Foundation observes that the boundary between "standard editing" and "going beyond standard editing" is, in many real deployments, the subject of legitimate disagreement. The Guidelines provide helpful examples at paragraphs (85) to (86), but the underlying assessment ("changes in the content that affect its meaning, style or intent") is necessarily case-specific. In disputed cases, the question of whether the exception applies will turn on the evidence available to the deployer or provider about what the AI system actually did. The Foundation respectfully suggests that the Guidelines could productively note that retention of contemporaneous records of the editing operation — including the input, the output, and the system configuration at the time of the operation — can assist providers and deployers in demonstrating the applicability of the exception. The Foundation does not propose that such retention be mandatory.

### On §4.4 — Interplay with other Union legal acts, paragraphs (88) to (92)

**On paragraph (88) — data protection compliance of marking solutions.** The Foundation strongly supports the requirement that marking and detection solutions must comply with EU data protection law, including data protection by design and by default, data minimisation, limited storage, security, and confidentiality. We observe that out-of-band cryptographic receipt approaches can be designed to be GDPR-compatible in straightforward ways: by anchoring only cryptographic digests of canonical metadata (rather than personal data itself), by relying on append-only ledgers in which no personal data is written, and by using key-rotation as the operative mechanism for the right-to-erasure analogue where deployer identification is involved. The Foundation respectfully observes that the Guidelines could productively note that the choice of marking and detection technique itself has data protection implications, and that providers should consider these implications at the design stage.

---

## Section VI — Article 50(4) AI Act: Labelling of Deep Fakes and certain text publications

### On §6.1.2 — The disclosure obligation under Article 50(4), subparagraph 1, paragraph (110)

The Foundation supports the principle articulated at paragraph (110) that labelling or disclosure under Article 50(4) subparagraph 1 should be understandable and perceivable by natural persons without their needing to rely on specific technical tools. This human-facing requirement is correctly distinguished from the machine-readable marking obligation in Article 50(2).

We observe — for symmetry with our comments on §3.1.2 — that the human-facing labelling is what discharges the substantive obligation, while machine-readable evidence (records that the labelling was applied, by whom, and when) is what enables the deployer to demonstrate compliance. Both are relevant; the Guidelines correctly require the first; the Foundation respectfully suggests the Guidelines could helpfully recognise the legitimacy of the second.

### On §6.1.3 — Transparency of artistic, creative, satirical, fictional or analogous deep fake content, paragraphs (111) to (116)

**On paragraph (114) — the "evidently" qualifier.** The Guidelines correctly observe that the "evidently" qualifier excludes content whose nature is potentially unclear or ambiguous to the audience. The Foundation supports this formulation and observes that the adversarial case — in which a deployer claims an artistic or satirical purpose for content that was understood by part of the audience as authentic — will be the substantive battleground of Article 50(4) enforcement in the first years.

The Foundation respectfully suggests that the Guidelines could productively note that the deployer asserting the "evidently artistic" defence bears the burden of demonstrating, on the facts of the specific publication, that the artistic, creative, satirical or fictional character was in fact evident at the time of publication and to the audience reasonably foreseeable at the time of publication. Contemporaneous evidence of the deployer's design choices, distribution context, and audience-targeting decisions will, in disputed cases, be load-bearing.

**On paragraph (116) — safeguards for third-party rights and freedoms.** The Foundation supports the strict reading: that the attenuated transparency obligation does not justify failure to respect personal-image, intellectual-property, or data-protection rights. We observe that effective protection of third-party rights in adversarial cases will, again, depend on the availability of contemporaneous evidence of when content was published, by whom, and in what form. The Foundation does not propose any change to paragraph (116) as drafted.

### On §6.2.1 — Text published with the purpose of informing the public on matters of public interest, paragraph (123)

The Foundation supports the broad, open-ended formulation of "matters of public interest" at paragraph (123). The non-exhaustive list (public administration and services, fundamental rights, public health, environmental protection, consumer safety, and economic, political, scientific or cultural developments with potentially important public implications) is well-judged. We observe that the application of this category to financial-services disclosures, corporate reporting, and supervised-sector communications (banking, insurance, securities markets) is, on the natural reading of the Guidelines, in scope. The example at the second bullet of paragraph (123) (AI-manipulated corporate reports published on a listed company's website containing investor information) confirms this reading. The Foundation supports this confirmation as it has substantial implications for the financial-services and regulated-industry deployment landscape and is correctly handled by the draft.

### On §6.2.3 — Exception from the transparency obligation for text under human review or editorial control, paragraphs (125) to (128)

This paragraph is, in the Foundation's respectful assessment, the single most consequential evidentiary provision in Article 50(4) for the financial-services, media and regulated-industry sectors. The exception's substantive requirements — deliberate examination of the substance of the content by competent natural persons, and editorial responsibility held by a legal or natural person — are correctly drawn.

**On paragraph (127) — superficial checks insufficient.** The clarification that superficial, solely formal or procedural checks, mere existence of an editorial policy, or cursory editorial approval without substantive engagement cannot fulfil the exception, is critically important and the Foundation supports it without qualification. We observe that the supervisory authority faced with a dispute over the applicability of the exception will require evidence of *who* performed the review, *when* it was performed, and *what* substantive engagement took place. Today, such evidence is typically retained in deployer-internal editorial workflow systems, content-management systems, or e-mail. Such records are accessible to the deployer; they are not generally externally verifiable.

**On paragraph (128) — editorial responsibility.** The Foundation strongly supports the requirement that the identity and contact details of the legal or natural person with editorial responsibility be made publicly available in an easily findable location. This is the right structural answer. We respectfully observe that the same logic — that accountability requires identifiable, externally verifiable assertion of responsibility — applies, *mutatis mutandis*, to the underlying review event itself.

**Foundation contribution to §6.2.3.** The Foundation respectfully invites the Commission to consider, for the final Guidelines, a clarification along the following lines (offered for the Commission's consideration, not as a proposed redline):

> *Where the deployer relies on the exception in Article 50(4), subparagraph 2, the deployer should be in a position to demonstrate, in the event of a dispute or a request from a competent authority, that the conditions for the exception were satisfied with respect to the specific publication at issue. Evidence may take various forms, including internal editorial workflow records, signed attestations from the natural person performing the human review, or externally verifiable cryptographic records of the review and editorial-control event. The choice of evidentiary form is at the deployer's discretion. The Guidelines do not prescribe any particular technique; the substantive question is whether the conditions for the exception were in fact satisfied with respect to the specific publication.*

The Foundation observes that the editorial-control exception in §6.2.3, as drafted, presumes the existence of an evidentiary infrastructure for editorial review that does not consistently exist across deployers today. For established media organisations under European Media Freedom Act regimes, robust editorial workflows are in place. For other deployers within the scope of Article 50(4) subparagraph 2 — financial-services issuers publishing investor-facing communications, public-administration agencies publishing public-safety information, scientific publishers handling AI-assisted research outputs — the evidentiary infrastructure is uneven. An open-protocol approach to producing externally verifiable records of editorial-review events would, in our respectful submission, enable the consistent application of the exception across this heterogeneous landscape. The Foundation makes no proposal that the Commission prescribe any particular approach, but invites the Commission to recognise the evidentiary gap and to leave space, in the Guidelines, for emerging open-protocol approaches to fill it.

---

## Section VII — Horizontal requirements applicable to the information provided under Article 50(5) AI Act, paragraphs (130) to (133)

### On §7.1 — Information provision in a clear and distinguishable manner, paragraph (131)

The Foundation supports the formulation that information is provided in a clear manner where it is noticeable and easy to understand, and in a distinguishable manner where it is easy to identify as separate from other information and the surrounding environment. The clarification that information buried in manuals or hidden in menu options does not satisfy the obligation is correct and important.

We respectfully observe that paragraph (131) addresses the *substantive* provision of information to the natural person, not the *evidentiary* posture of the provider or deployer who must demonstrate that the information was so provided. As with our comments on §§3.1.2, 4.2.1 and 6.1.2, we observe that the substantive obligation and the evidentiary posture are distinct and complementary.

### On §7.2 — First interaction or exposure, paragraph (132)

The Foundation supports the clarification at paragraph (132) that the "first interaction or exposure" applies to each natural person, not only the first natural person encountering the system or its output. The corollary observation that disclosure must accompany each output to each natural person exposed is a substantial evidentiary commitment, and the Foundation supports it. We observe, however, that this scaled obligation amplifies the evidentiary gap noted in earlier sections: providers and deployers will, in practice, need scalable mechanisms for demonstrating that disclosure was effective at the moment of each first exposure to each natural person.

### On §7.3 — Compliance with applicable accessibility requirements, paragraph (133)

The Foundation supports the cross-reference to Directive 2016/2102 and Directive 2019/882 (the European Accessibility Act). The clarification that Article 50 AI Act does not impose distinct or additional accessibility requirements is correct and the Foundation has no comment beyond noting our support for this formulation.

### Foundation contribution to Section VII

The horizontal requirements of Section VII apply, by their structure, to all four substantive obligations under Article 50(1) to (4). The Foundation respectfully invites the Commission to consider adding a new horizontal paragraph at the end of Section VII, addressing the evidentiary dimension of the horizontal requirements. We offer the following formulation for the Commission's consideration:

> *7.4. Demonstrability of compliance. Providers and deployers subject to the obligations in Article 50(1) to (4) AI Act should be in a position to demonstrate, in the event of a request from a competent authority under Article 50 or under the broader market surveillance framework, that the information required by the relevant provision was provided to the natural persons concerned in conformity with the horizontal requirements of Article 50(5). The form of such demonstration is at the discretion of the provider or deployer. Acceptable forms of demonstration include, without limitation: design-time documentation accompanied by configuration records sufficient to establish that the design-time mechanism was operative at the relevant moment; server-side logs and telemetry retained by the provider or deployer; and externally verifiable, cryptographically signed records of the disclosure event. Externally verifiable evidentiary infrastructure, where used, may rely on open standards and may be operated as a public good; the Guidelines do not prescribe any particular technique, supplier or operator.*

This formulation, offered for the Commission's consideration, accomplishes three things. It recognises that compliance must be demonstrable, not merely asserted. It is technology-neutral, contemplating multiple forms of demonstration. It leaves open, without endorsing or preferring, the development of externally verifiable evidentiary infrastructure as one possible compliance mechanism. The Foundation makes no proposal that any particular protocol, vendor, or implementation be recognised or preferred.

---

## Three specific requests of the Commission

In light of the foregoing, the Foundation respectfully makes the following three specific requests of the Commission.

### Request 1 — Recognition of externally verifiable cryptographic receipt evidence as one compliant means of evidencing Article 50 obligations

The Foundation respectfully requests that the final Guidelines acknowledge, in technology-neutral language, that externally verifiable cryptographic receipt evidence is one of multiple permissible means by which providers and deployers may evidence compliance with the obligations under Article 50(1), Article 50(2), and Article 50(4). The Foundation does not request that any particular implementation, protocol or operator be recognised, listed, or preferred. The Foundation requests only that the categorical legitimacy of externally verifiable evidence — alongside design-time documentation, internal logs, and other accepted forms — be made explicit. This recognition reduces regulatory uncertainty for providers and deployers who wish to invest in externally verifiable compliance mechanisms, and reduces the supervisory burden on competent authorities who would benefit from receiving compliance evidence in a form that does not require access to the regulated entity's internal systems.

### Request 2 — Addition of a horizontal demonstrability paragraph to Section VII

The Foundation respectfully requests that the Commission consider the addition of a horizontal paragraph at the end of Section VII, addressing the demonstrability of compliance with the obligations in Article 50(1) to (4). A draft formulation is offered above. The drafting is a matter for the Commission; the substantive point is that the horizontal requirements should contemplate not only the substantive provision of information to natural persons, but also the means by which compliance with that provision may be demonstrated to competent authorities. Externally verifiable evidentiary infrastructure should be recognised as one of multiple compliant means.

### Request 3 — Opening of a coordinated follow-up consultation on evidentiary infrastructure for Article 50

The Foundation respectfully requests that the Commission consider opening a follow-up consultation, in due course and in coordination with the relevant standards processes, on the question of evidentiary infrastructure for Article 50. We suggest that such a consultation would benefit from coordination with at least the following parallel processes:

- The IETF Supply Chain Integrity, Transparency and Trust (SCITT) Working Group, where work directly relevant to AI-deployment evidentiary infrastructure is in progress;
- CEN-CENELEC JTC 21 (Artificial Intelligence), the European standards body to which the Commission's standardisation request M/593 is addressed and which is developing harmonised standards relevant to AI Act compliance;
- ISO/IEC JTC 1/SC 42 (Artificial Intelligence), the international counterpart standards body whose work on AI trustworthiness and management systems is complementary; and
- The Commission's own work on the Code of Practice for general-purpose AI systems, where the transparency chapter intersects substantially with Article 50 implementation.

A coordinated consultation across these processes would, in our respectful submission, accelerate the development of a shared technical baseline for Article 50 evidentiary infrastructure and reduce the risk of fragmentation across Member States and across sectors. The Foundation offers to contribute substantively to any such consultation through its participation in each of these standards processes.

---

## Institutional disclosure and offer of follow-up engagement

LedgerProof Foundation is a public-interest, in-formation US 501(c)(3) public charity (Delaware, in formation), with a Dutch Stichting subsidiary in formation (Amsterdam, under counsel of NautaDutilh) serving as the European contractual counterparty. The Foundation stewards the LedgerProof Protocol, an open, royalty-free cryptographic protocol for evidencing AI-deployment governance events within the scope of Article 50 of Regulation (EU) 2024/1689. Reference implementations are published under the Apache 2.0 licence at the Foundation's public code repository. The protocol is on the IETF SCITT track as Internet-Draft `draft-dawkins-scitt-ai-article50-00`, published on the IETF Datatracker. The Foundation is engaged with CEN-CENELEC JTC 21 through a DIN SME membership application currently in preparation, and with ISO/IEC JTC 1/SC 42 through mirror activities. An independent cryptographic audit of the protocol's reference implementations is scheduled for publication later in 2026.

The Foundation makes no claim of Commission endorsement and does not seek inclusion in any regulator-published reference list. This submission is offered as a public-interest contribution to the consultation record. The Foundation's IP licence over the protocol is perpetual, royalty-free, irrevocable, and non-exclusive; any third party may implement the protocol under the same terms. The Foundation's Board of Directors, none of whom hold equity in any commercial implementer of the protocol, will be confirmed by the end of August 2026, and Foundation governance documents (Conflict of Interest Policy, IP Transaction Committee Charter, Foundation Advisory Council Charter) are published as anchored public records on adoption.

The Foundation is at the Commission's disposal for follow-up engagement on any aspect of this submission. We are particularly available to provide technical clarification on the proposals offered in this document, to participate in any working group or workshop the Commission convenes on Article 50 evidentiary infrastructure, and to coordinate with the Commission on the parallel standards processes identified above.

**Foundation contact for this submission:**
LedgerProof Foundation
foundation@ledgerproof.org

**Public references:**
- IETF Internet-Draft: `https://datatracker.ietf.org/doc/draft-dawkins-scitt-ai-article50/`
- Foundation transparency page: `https://ledgerproofhq.io/foundation`
- Open code repository: `https://github.com/ledgerproof`

The Foundation thanks the Commission, the Artificial Intelligence Office, and the consultation team for the opportunity to contribute to this important regulatory work.

---

*End of submission.*

---

# APPENDIX — Pre-submission checklist for Veronica (NOT part of the submitted text)

Before submitting on Futurium tomorrow morning, please verify the following:

- [ ] **Form field — First name + Surname + E-mail address**: fill in personally on the Futurium form (these are not in the submission text by design).
- [ ] **Form field — Submitter category**: "Organisation" — selected.
- [ ] **Form field — Organisation name**: "LedgerProof Foundation" — exactly as written.
- [ ] **Form field — Country of establishment**: select per the form's available options; the Foundation is US 501(c)(3) (Delaware) with Dutch Stichting subsidiary (Amsterdam). If the form requires one selection, "United States" is the primary establishment; the Dutch Stichting can be referenced in the Activities description and is referenced in the submission body.
- [ ] **Form field — Activities description**: the "Activities description (intended for the form's 1,300-character field)" section above is drafted to fit within 1,300 characters including spaces. Paste verbatim from that section. Verify the character count in the Futurium form's input box before submitting; the form may count newlines differently than the source file. Trim trailing whitespace if needed.
- [ ] **Form field — Sections being addressed**: select Section II, Section III, Section IV, Section VI, Section VII. (Do NOT select Section V — the Foundation has no substantive comment on Article 50(3) and selecting it dilutes the focused contribution.)
- [ ] **Body paste**: the body submission begins at "Preamble — purpose and discipline of this submission" and ends at "*End of submission.*". Do NOT paste the header block, the activities-description block, or this appendix.
- [ ] **Paragraph numbering accuracy**: every paragraph reference in the submission body (paragraph (29), paragraph (30), paragraph (33), paragraph (35), paragraph (37), paragraph (39), paragraph (42), paragraph (47), paragraph (49), paragraph (67), paragraph (69), paragraph (70), paragraph (72), paragraph (74), paragraph (75), paragraph (76), paragraph (78), paragraph (83), paragraph (84), paragraph (88), paragraph (110), paragraph (111), paragraph (114), paragraph (116), paragraph (123), paragraph (125), paragraph (127), paragraph (128), paragraph (130), paragraph (131), paragraph (132), paragraph (133)) has been cross-checked against the draft Guidelines text at `/tmp/article50_guidelines.txt`. If the Commission publishes a re-paginated or re-numbered version between now and the submission deadline, the references should be re-verified.
- [ ] **No PII**: no e-mail addresses other than the Foundation's institutional contact `foundation@ledgerproof.org`. No personal names beyond the IETF draft identifier `draft-dawkins-scitt-ai-article50-00` (which is the public draft identifier and not PII).
- [ ] **No confidential information**: no operating-model financial detail, no Founding Member or Strategic Beta Partner identifiers, no internal threat-model detail, no commercial-counterparty names, no audit-firm names (the audit reference says "scheduled for publication later in 2026" without naming firms; this is correct).
- [ ] **No customer or vendor name-drop**: Klarna, Adyen, ING, Wise, Allianz, Riot, Mistral, NCC Group, Trail of Bits, Cure53, Hercules Capital, Qatalyst, NautaDutilh (note: NautaDutilh IS named as Foundation counsel for the Dutch Stichting in the institutional identification block — this is appropriate institutional disclosure, not vendor name-drop). Verify no other names slipped in.
- [ ] **C1 — no claim of regulator endorsement**: verified. The submission explicitly disclaims this at the institutional-disclosure section and frames itself throughout as a public-interest contribution.
- [ ] **C1 — no claim of Article 40 presumption of conformity**: verified. The submission does not assert presumption of conformity. The reference to harmonised standards processes is descriptive of where the Foundation participates, not a claim that the Foundation's protocol confers presumption of conformity.
- [ ] **C2-C8 — no claim of integration with infrastructure not yet shipped**: verified. The reference to reference implementations describes published Apache 2.0 code; the audit reference is appropriately framed as scheduled, not complete.
- [ ] **Foundation in-formation status**: disclosed in the institutional identification block (both US and Dutch entities), in the Activities description, and in the closing institutional disclosure. Verified.
- [ ] **Voice — institutional, not founder-personal**: re-read the submission for any "I," "we are excited to," "thrilled to," "delighted to," or similar founder-personal phrasing. The submission uses "the Foundation" or "the Foundation respectfully" throughout. Verified.
- [ ] **European-English register**: verify spellings — organisation (not organization), harmonised (not harmonized), authorisation (not authorization), categorisation, recognised, characterised, etc. Verified in draft; re-verify after any edits.
- [ ] **Length**: target 4,000-6,000 words for the substantive submission (excluding this appendix). Current word count of the submission body is within this range. If trimming is needed, the Section II commentary and the §3.3 commentary are the most easily compressed without losing the load-bearing substantive contributions.
- [ ] **Three specific requests are clearly labelled and numbered**: verified.
- [ ] **Foundation contact e-mail consistent**: `foundation@ledgerproof.org` throughout. Verified.
- [ ] **IETF Datatracker URL accuracy**: verify the URL resolves to the live draft before submission.
- [ ] **GitHub repository URL accuracy**: verify the repository URL is the canonical Foundation repository, not a personal fork.
- [ ] **Time discipline**: consultation closes tomorrow, 3 June 2026. Submit Wednesday morning Brussels time with a buffer of at least three hours before the close to allow for platform issues. Do not leave for the final hour.

**Final note before submission.** This is the Foundation's institutional debut on the EU AI Act Article 50 record. The submission will be a public document on the consultation record and will be citable in the final Guidelines, in academic literature, and in subsequent Foundation correspondence with the Commission and with national competent authorities. The Foundation's standing in subsequent regulatory engagement — including the forthcoming Code of Practice consultation submission, the DIN SME New Work Item Proposal, and any subsequent EU AI Office working-group invitation — will rest in part on the quality and discipline of this first contribution. The submission has been drafted with this in view.
