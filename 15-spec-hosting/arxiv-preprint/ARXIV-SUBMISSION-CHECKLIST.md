# arXiv submission checklist — OCPP-AI v1.0

**Submission window**: Tonight (Wed Jun 3, 2026) before midnight PDT.
**Why tonight**: claims today's date as the canonical citation; SCITT mailing-list post + Politico EU pitch + Stibbe brief all reference the arXiv submission as live.

## Step 1 — Log in to arXiv

URL: https://arxiv.org/submit
- If V doesn't have an arXiv account: create one. Email verification takes ~5 min.
- If V doesn't have submission privileges (some arXiv categories require endorsement): cs.CR requires NO endorsement for first submission by an unaffiliated author IF the abstract is technically substantive. This submission qualifies.

## Step 2 — Submission metadata (paste these directly into arXiv's form)

**Title**:
```
An Open Cryptographic Provenance Protocol for AI System Outputs (OCPP-AI): Substrate-Agnostic Article 50 Transparency Receipts Compatible with eIDAS 2.0 and the European Blockchain Services Infrastructure
```

**Authors**:
```
Veronica S. Dawkins
```

**Author affiliation**:
```
LedgerProof Foundation (in formation)
```

**Author email**: `veronica@ledgerproofhq.io`

**Primary subject classification**: `cs.CR` (Cryptography and Security)

**Cross-list classifications**:
- `cs.CY` (Computers and Society)
- `cs.DC` (Distributed, Parallel, and Cluster Computing)

**Comments line** (free text — short note about the paper):
```
24 pages, 0 figures. Specification artifacts at https://spec.ledgerproofhq.io. IETF SCITT WG track: draft-dawkins-scitt-ai-article50-00.
```

**License**: `CC BY 4.0` (select from arXiv's license dropdown — "Creative Commons Attribution 4.0 International")

**Abstract** (paste from line 22-46 of `ocpp-ai-v1.tex`, or use the version below — they match):
```
Article 50 of Regulation (EU) 2024/1689 (the "EU AI Act") imposes transparency obligations on providers and deployers of AI systems with respect to natural persons, supervisory authorities, and the public. Operational implementation requires machine-readable evidence that survives the continued cooperation of any single deployer, vendor, or jurisdiction. Existing vendor-proprietary logging mechanisms fail this requirement by structurally coupling enforcement evidence to individual cloud platform operators outside Union jurisdiction. This paper specifies the Open Cryptographic Provenance Protocol for AI System Outputs (OCPP-AI), a substrate-agnostic protocol for machine-readable cryptographic receipts addressing Article 50 sub-obligations 50(1), 50(2), 50(4), and 50(6). The protocol separates an Anchor Interface specification (defining the properties any conforming anchor substrate must satisfy) from substrate-specific reference implementations: Bitcoin OP_RETURN as the current reference implementation and the European Blockchain Services Infrastructure (EBSI) as the primary enterprise-government alternative. We demonstrate architectural compatibility with W3C Verifiable Credentials 2.0 through a published JSON-LD context that wraps OCPP-AI receipts as Verifiable Credentials without loss of information, and architectural complementarity with Regulation (EU) 2024/1183 (eIDAS 2.0) through a composition pattern that enables qualified evidence presentation through established Qualified Trust Service Providers without modification of the core receipt format. The specification preserves GDPR Article 17 erasure mechanics through structural exclusion of personal data at the receipt schema validation layer and at the anchor payload format. Reference implementations exist in Python, TypeScript, and Rust under Apache License 2.0, with twenty-nine framework adapters covering the principal AI orchestration ecosystems. We propose OCPP-AI for stakeholder consultation at the European Commission AI Office, the European AI Board, CEN-CENELEC Joint Technical Committee 21, and the IETF SCITT Working Group.
```

## Step 3 — Upload the source files

arXiv accepts a single .tex file OR a .tar.gz with all sources. Single .tex is simpler here since there's only one file.

**File to upload**: `15-spec-hosting/arxiv-preprint/ocpp-ai-v1.tex` (this repo's path; full filesystem path: `/Users/veronicadawkins/Documents/LedgerProof-Launch-July6/15-spec-hosting/arxiv-preprint/ocpp-ai-v1.tex`)

arXiv will compile server-side using their pdflatex install. Compilation takes ~30-90 seconds. arXiv shows the compiled PDF for review before final submission.

## Step 4 — Preview + submit

- arXiv shows the rendered PDF after server-side compilation
- Verify the title, author block, abstract, and bibliography render correctly
- If anything fails to compile: send me the arXiv error log and I'll fix the .tex inline
- Click "Submit" when satisfied
- arXiv returns a temporary identifier (`submit/XXXXXXXX`) immediately; the permanent `arXiv:YYMM.NNNNN` ID is assigned overnight during arXiv's daily moderation pass

## Step 5 — After submission

Within ~24 hours arXiv assigns the permanent ID. The moment you have that ID:

1. **Forward it to me** so I can update the IETF SCITT mailing-list post + Politico EU pitch + Stibbe brief to cite the live arXiv URL
2. **Update the Foundation governance event record** `15-spec-hosting/governance-events/gov-2026-06-03-dgcnect-memo.json` to include the arXiv ID
3. **Add a citation to the OCPP-AI v1 spec** at the bottom of Article 10 — "This specification is accompanied by arXiv preprint arXiv:YYMM.NNNNN"

## What can go wrong (and what to do)

| Issue | Action |
|-------|--------|
| arXiv account requires endorsement for cs.CR | cs.CR no longer requires endorsement for first submission since 2020 policy change; if the system asks, request endorsement from the SCITT WG co-chairs (Henk Birkholz, Hannes Tschofenig) or from any prior arXiv submitter in cryptography |
| LaTeX compilation fails | Send me the arXiv error log. Common fixes: hyperref placement, encoding, missing package declarations |
| Title too long for arXiv form | Truncate to "Open Cryptographic Provenance Protocol for AI System Outputs (OCPP-AI): Substrate-Agnostic Article 50 Transparency Receipts" — drop the eIDAS 2.0 / EBSI qualifier from the title only |
| Wrong CC license selected | arXiv allows post-submission license correction within 24 hours; email arxiv-help@arxiv.org if missed |
| Submission lands but doesn't appear on schedule | arXiv announces new submissions at 20:00 EDT daily; submissions after 14:00 EDT appear next day's listings. Tonight's PDT submission window aligns with arXiv tomorrow's listings (June 4 EDT) — perfectly fine timing for the institutional outreach Monday Jun 9 |

## Why this matters strategically

The arXiv ID is the institutional credibility marker that converts the memo from "Foundation submission" to "academic preprint citable in regulatory consultations." DG-CNECT, EAIB, CNIL, BfDI, and Big-4 legal advisory teams routinely cite arXiv preprints in policy analysis. The IETF SCITT mailing-list post and the Politico EU pre-pitch both anchor their credibility framing on the arXiv submission being live.

**The submission is the highest-leverage 15-minute action available between now and Monday Jun 9.**
