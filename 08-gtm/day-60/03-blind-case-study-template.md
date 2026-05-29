# Blind Case Study Template

**Purpose:** A pre-built case study skeleton ready to fill the moment a reference customer agrees to be named. Keeps time-to-publish under 14 days from agreement.

**Use:** Fill bracketed values. Send draft to customer communications for review. Publish to `ledgerproofhq.io/case-studies/` and link from the master GTM plan.

---

# Case Study: [Customer Name] — Article 50 receipts in production at [scale descriptor]

**Sector:** [FSI / Media / Industrial / Pharma / Telecom / Retail]
**EU jurisdiction:** [Germany / France / Netherlands / Italy / Spain / Ireland / multi-EU]
**Article 50 sub-clauses in scope:** [50(1) / 50(2) / 50(4) / combination]
**Deployment date:** [ISO 8601]
**Production scale:** [N] receipts per [day/month] across [M] AI-touched workflows

---

## The challenge

[Customer] operates [brief description of business] across [N] EU member states. By early 2026, [Customer]'s use of generative AI had expanded from [original use case] to [N] distinct production workflows, including [workflow examples].

In Q1 2026, [Customer]'s [Chief Risk Officer / Chief Compliance Officer / General Counsel / Head of AI Infrastructure] surfaced three concerns to the executive committee:

1. **Inventory uncertainty.** [Customer] did not have a single source of truth for which AI systems were deployed, by which business unit, against which regulation.
2. **Article 50 enforcement risk.** With enforcement landing August 2, 2026, the executive committee required a demonstrable audit trail for each AI-generated output covered by Article 50.
3. **Procurement velocity.** [Customer]'s own enterprise customers had begun requesting AI compliance evidence in their RFPs. The lack of a verifiable answer was lengthening sales cycles by [N] weeks.

## Why LedgerProof

[Customer]'s evaluation considered [N] vendors and approaches. LedgerProof was selected on four grounds:

1. **Open protocol.** [Customer] required an implementation it could continue to use if the vendor failed. LedgerProof's IETF Internet-Draft and Foundation governance satisfied that requirement.
2. **Live in production at evaluation time.** [Customer] required evidence of a working production deployment, not a roadmap. LedgerProof had been operating receipt issuance continuously since May 18, 2026.
3. **Foundation-governed.** [Customer]'s legal review surfaced that any single-vendor solution would not pass procurement at [Customer]'s scale. The LedgerProof Foundation structure passed.
4. **Standards mapping.** LedgerProof's published mapping documents (ISO/IEC 42001, NIST AI RMF, DORA Article 28) gave [Customer]'s internal audit team a defensible framework for AIMS evidence.

## Deployment

| Phase | Duration | Outcome |
|---|---|---|
| 30-Day Pilot | [Day X – Day X+30] | [N] AI outputs receipted; P99 latency [X] ms; operator availability [X]%; Audit-Ready Compliance Stamp PDF delivered |
| Production roll-out — wave 1 | [duration] | First [M] workflows in production; [N] receipts/month |
| Production roll-out — wave 2 | [duration] | All [M] workflows in production; [N] receipts/month |
| Steady state | ongoing | [N] receipts/month; monthly Audit-Ready Compliance Stamp PDF delivered to [Customer]'s GC |

**Technical integration:**
- SDK: [`ledgerproof` Python / `@ledgerproof/sdk` TypeScript / both]
- Integration touchpoints: [list workflows and their integration shape]
- Latency overhead measured: P99 [X] ms (SLO ≤ 50 ms)
- Operator availability measured: [X]% (SLO ≥ 99.5%)

**Compliance integration:**
- ISO/IEC 42001 Annex A controls covered: [N] of 38, including all 8 in A.6 AI System Life Cycle
- DORA Article 28 third-party risk evidence: [Customer]'s ICT third-party register cross-references receipt issuance
- Internal audit cycle: receipts integrated into [Customer]'s [GRC platform — ServiceNow / MetricStream / RSA Archer / etc.]

## Results

**Compliance posture (Day 90 post-deployment):**
- [N] AI outputs receipted with zero missed anchor commitments
- [N] Audit-Ready Compliance Stamp PDFs delivered to GC for monthly Board reporting
- 1 regulator interaction completed with the Stamp PDF as primary evidence (outcome: [favorable / no further action / informational only])
- [N] internal audit cycles closed with LedgerProof Receipts as the AIMS A.6 evidence layer

**Operational impact:**
- [Customer]'s enterprise RFP response time reduced by [N] weeks because the AI compliance section now points to the verifier portal
- [Customer]'s AI Inventory increased by [N] discovered workflows during deployment (workflows not previously catalogued)
- [Customer]'s [Chief Risk Officer / GC] reported [X] hours/week reduction in ad-hoc executive briefing requests on AI exposure

**Procurement velocity (where applicable):**
- [€N M] of previously stalled enterprise pipeline closed in the [N] weeks post-deployment, with AI compliance evidence cited by [Customer]'s sales team as unblocking

## In their own words

> "[Customer quote — 1–2 sentences from the reference contact, factually describing experience, not endorsing LedgerProof in marketing language. Reviewed and approved by Customer communications.]"
>
> — [Name, title], [Customer]

## What's next

[Customer] is expanding the deployment to cover [additional workflows] in [timeframe]. [Customer] has also [contributed to the IETF working group / joined the Foundation Advisory Council / participated in a joint Big-4 client webinar] as part of its broader Article 50 posture.

---

## Publication checklist

- [ ] Customer communications review and approval received in writing
- [ ] Customer legal review for accuracy
- [ ] All numeric claims verifiable against LedgerProof's own internal data
- [ ] Customer name and logo use approved per Customer brand guidelines
- [ ] Quote approved by named individual
- [ ] Permission to use case study in investor materials separately confirmed
- [ ] Case study anchored as a LedgerProof Receipt for tamper-evidence
- [ ] Case study added to verifier portal as a public Foundation artifact
- [ ] Case study URL added to `ledgerproofhq.io/case-studies/` and master GTM plan index

## Authorized uses (per signed agreement)

| Use | Default | Requires separate approval |
|---|---|---|
| ledgerproofhq.io case studies page | ✓ | — |
| One-pager attached to outbound emails | ✓ | — |
| Investor diligence pack | ✓ | — |
| Press release quotes | — | ✓ |
| Big-4 partner co-branded materials | — | ✓ |
| Public conference panels | — | ✓ |
| Translation to other languages | — | ✓ |

## Refresh cadence

Case studies are refreshed every 6 months with updated metrics. Customers may request retraction at any time with 30 days notice; LedgerProof commits to taking down case studies within 5 business days of a retraction request.
