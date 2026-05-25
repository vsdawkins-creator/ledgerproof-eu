# Verisk -- Strategic Partnership Package (NOT equity)

## Contact
**To:** Yang Chen -- Head of Corporate Development & Strategy, Verisk
**Email:** yang.chen@verisk.com
**Type:** Strategic corporate partnership
**Attach deck:** No

## Subject
LedgerProof + Verisk: provenance receipts for AI-generated insurance analytics

## Email body

Dear Verisk AI Partnerships Team,

In May 2026, Verisk announced that its insurance analytics are available through Claude via standardized MCP connectors. That integration means Verisk is now producing AI-generated insurance analytics outputs at scale, delivered directly into underwriting and risk decision workflows.

LedgerProof is the provenance layer that makes those outputs permanently verifiable.

When a Verisk AI analytics output is used in an underwriting decision, a regulatory filing, or a coverage determination, the downstream question is verifiability: what was produced, by what system, with what data, and at what moment. Today, the answer depends on Verisk's internal records. LedgerProof changes that. We anchor the SHA-256 hash and Ed25519 signature of any document to Bitcoin mainnet via OP_RETURN at the moment of creation. The result is an LPR v1.0 receipt -- a tamper-evident, permanently verifiable record that exists on Bitcoin mainnet regardless of what any internal system shows later. Live since May 18, 2026: https://verify.ledgerproofhq.io/r/founding-declaration

The regulatory driver is concrete. EU AI Act Article 50 enforcement begins August 2, 2026, requiring machine-verifiable provenance on AI-generated content. Verisk's European insurance clients will face this requirement directly. A LedgerProof receipt embedded in every Verisk AI analytics output satisfies that requirement automatically.

The integration architecture is lightweight. LedgerProof operates as a receipt-generation layer: Verisk passes the document hash at output time, we anchor it to mainnet and return a verifiable receipt URI. No latency impact on analytics delivery. No changes to Verisk's core data infrastructure. Revenue model: per-receipt with enterprise volume tiers.

This is an integration and partnership inquiry. I would welcome a technical conversation with the appropriate team to map the integration surface and timeline.

Veronica S. Dawkins
Founder & CEO, LedgerProof, Inc.
veronica@ledgerproofhq.io

---
## Notes
- Verisk: $5B ARR insurance analytics; just integrated with Claude via MCP (May 2026)
- Yang Chen: Head of Corporate Development & Strategy -- best fit for partnership
- Email: yang.chen@verisk.com (First.Last@verisk.com confirmed pattern)
- Strategic partnership inquiry only -- no equity ask, no deck
- The Claude/MCP integration is the key hook
- Send date: May 21, 2026
