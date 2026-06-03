---
title: Security disclosure policy
description: How to report a security vulnerability in the LedgerProof Protocol, reference implementations, or Foundation infrastructure. Coordinated disclosure terms, response SLAs, and acknowledgment policy.
---

> **Status:** This page is the public security disclosure policy of the LedgerProof Foundation (in formation). It governs vulnerability reports against the LedgerProof Protocol specification, the reference Python/TypeScript/Rust implementations, and Foundation-operated infrastructure. It does NOT govern vulnerabilities in third-party adapters or downstream deployer systems — those are owned by their respective publishers.
>
> **Last reviewed:** 3 June 2026 · **Next scheduled review:** before 6 September 2026

## Scope

In scope:

- The **LedgerProof Protocol** specification (`draft-dawkins-scitt-ai-article50-00` and successors, the LPR v1.1 schema, the OP_RETURN format `LPR1 || merkle_root_32`)
- The **reference implementations** at `github.com/vsdawkins-creator/ledgerproof-eu` (Python, TypeScript, Rust packages and the 29 adapters)
- **Foundation-operated infrastructure**: this site (`docs.ledgerproofhq.io`), the spec site (`spec.ledgerproofhq.io`), the Foundation-published anchor verifier endpoint, the OpenTimestamps verifier integration
- **Foundation governance receipts** — the cryptographic integrity of receipt-anchored Foundation actions (board minutes, key rotations, charter ratifications)

Out of scope:

- Third-party adapters not maintained by the Foundation (we forward reports to maintainers but do not own response)
- Customer or deployer infrastructure (the LedgerProof protocol is verifier-side; deployer ops are the deployer's responsibility)
- Bitcoin Core itself, the OpenTimestamps calendar servers, or any other upstream dependency outside Foundation control (forwarded upstream)
- Social-engineering attacks against Foundation staff or contributors absent a technical control failure
- Denial of service against the verifier endpoint at typical residential bandwidth (operationally interesting, not a protocol vulnerability)

## How to report a vulnerability

**Email**: `security@ledgerproofhq.io` (preferred). PGP key fingerprint and signed acknowledgment of receipt under § Response SLAs below.

**Encrypted reporting**: If you require encrypted submission, request the current security team PGP key by emailing `security@ledgerproofhq.io` with subject line `PGP key request`. Auto-reply returns the current key fingerprint and full key block within one business day. Public key rotations are announced on this page and Bitcoin-anchored as Foundation governance events.

**What to include in your report:**

1. A clear description of the issue and the threat model it violates
2. Reproduction steps or a proof-of-concept (we accept text, code, packet captures, or signed binary blobs)
3. The affected component, version, and commit hash if reporting against the reference implementations
4. Your suggested CVSS 3.1 vector if you have one (we may revise)
5. Whether you intend to publish independently and your proposed timeline

**What we ask you NOT to do:**

- Do not test against deployer or customer infrastructure without explicit permission from that party
- Do not exfiltrate, retain, or share third-party data you encounter during testing
- Do not test against the live Bitcoin mainnet anchoring path in ways that incur >$500 in cumulative anchor fees without coordinating with us first

## Response SLAs

We commit to the following timelines, measured from receipt of a well-formed report at `security@ledgerproofhq.io`:

| Severity | Acknowledgment | Initial triage decision | Fix or mitigation target | Public disclosure target |
|----------|----------------|--------------------------|--------------------------|--------------------------|
| **Critical** (active exploitation, signing-key compromise risk, receipt forgery) | 24 hours | 72 hours | 14 days | 30 days post-fix |
| **High** (verifiable spec violation, denial of trust without active exploitation) | 48 hours | 7 days | 30 days | 60 days post-fix |
| **Medium** (degradation of verifier guarantees, recoverable without re-anchoring) | 72 hours | 14 days | 90 days | 90 days post-fix |
| **Low** (hardening opportunity, no current trust impact) | 7 days | 30 days | next scheduled release | bundled with release notes |

If we miss any of these SLAs, we publish the miss on this page in the **§ SLA Misses** section below within 7 days of the miss.

## What we will NOT do

- We will **never** request that you delay disclosure beyond the published targets above without giving you a written reason and a revised target
- We will **never** condition vulnerability acceptance on signing an NDA, contributing to LedgerProof Inc., or accepting Foundation employment
- We will **never** offer bug bounties scaled to embarrass reporters who decline to participate in a bounty program (see § Acknowledgment below for how we recognize reporters)
- We will **never** claim third-party endorsement of a fix that the third party has not actually issued

## Acknowledgment

If you confirm acceptance of a fix, you have three options for public credit, your choice:

1. **Named acknowledgment** in the published advisory and the `SECURITY-ADVISORIES.md` file at the project root (default)
2. **Pseudonymous acknowledgment** using a handle you supply
3. **No public acknowledgment** at your request

For reports that lead to a verified critical or high-severity fix, we additionally publish:

- A signed Foundation governance event (Bitcoin-anchored) recording the advisory and fix landing
- A CVE assignment via the LedgerProof Foundation CNA pool (in formation; until live, via MITRE)

We do not currently operate a paid bug bounty program. We expect to publish bounty terms post-launch (after 6 July 2026) once Foundation capital ratification is complete. Reports submitted before bounty terms are published are eligible for bounty payment under the terms in effect when the report was received, paid retroactively. Sign your report.

## Threat model

The LedgerProof protocol's security goals are stated in the IETF draft and reproduced here as the basis for severity scoring:

1. **Forgery resistance**: A receipt cannot be forged to attribute content to a deployer who did not sign it. *Threat: signing key compromise, signature scheme weakness, replay across receipt instances.*
2. **Tamper evidence**: A receipt cannot be modified post-issuance without invalidating the signature chain. *Threat: chain manipulation, prev_hash spoofing, sequence gap insertion.*
3. **Independent verifiability**: A receipt can be verified using only Bitcoin chain + Foundation public key + the receipt itself, with no SaaS dependency. *Threat: verifier required to call a non-Foundation endpoint, hidden state requirements, opaque format changes.*
4. **Anchor durability**: Anchored receipts remain verifiable as long as the Bitcoin chain remains accessible. *Threat: OP_RETURN parsing ambiguity, anchor format collision, OpenTimestamps proof corruption.*
5. **Privacy by structure**: Receipts do not embed PII; specifically, no email addresses, no government IDs, no biometric data, no free-text personally-identifiable narrative. *Threat: schema permits PII insertion at validation time, downstream tooling logs PII, anchor contains exfiltrable identifier.*

A finding that violates one or more of (1)-(5) is in scope. A finding that creates operational difficulty without violating one of (1)-(5) is in scope at lower severity.

## GDPR posture

The reference implementation enforces GDPR-friendly defaults at schema validation:

- `deployer_id`, `reviewer_role`, and `review_rationale` fields **reject** email addresses, phone numbers, and free-text patterns that match common PII regexes
- Bitcoin-anchored payload is bounded to `LPR1 || merkle_root_32` (36 bytes total) — no payload room for embedded identifiers
- Receipt body fields use hashes, opaque identifiers, and structured codes rather than narrative text

A schema or implementation change that weakens any of these properties is treated as a **High** severity disclosure.

If you discover a deployer using LedgerProof to anchor PII in violation of the schema, please report the deployer to the appropriate supervisory authority (CNIL, BaFin, AGCOM, etc.) — the Foundation does not have standing to compel third-party deployer remediation, and the deployer is the data controller under Article 4 GDPR. We will publicly support any supervisory authority enforcement action against PII-anchoring deployers.

## Coordinated disclosure with downstream maintainers

If the vulnerability you report affects a third-party adapter (the 29 framework adapters listed at `/developers/adapters/`), we coordinate the fix as follows:

1. We acknowledge your report under the SLA matrix above and triage severity
2. We forward the technical details (NOT your identity unless you authorize) to the affected adapter maintainer within 24 hours of triage
3. We track the maintainer's fix or non-response and publish the timeline in our advisory regardless of maintainer engagement
4. If the maintainer does not engage within 30 days of forward, we publish the unfixed vulnerability with a clear "no maintainer response" notice and an in-Foundation mitigation if one exists

We will not silently drop a vulnerability because the upstream maintainer declines to fix it. Quiet failure is incompatible with the verifier independence guarantee.

## Bitcoin anchoring failure modes

A specific subclass of vulnerability concerns the Bitcoin anchoring path. Examples of in-scope findings:

- An attack that causes the OpenTimestamps proof to validate against a different Merkle root than the one signed
- A condition under which the OP_RETURN format `LPR1 || merkle_root_32` can be confused with another protocol's OP_RETURN format in a way that misleads verifiers
- A weakness in the Foundation's signing key rotation path that allows backdated receipts to validate against the new key
- A timing condition in the anchor publication path that causes a receipt to claim anchoring before the Bitcoin transaction is mined

Reports against these classes are typically **Critical** or **High** severity.

## Out-of-band channels for active incidents

If you are reporting an actively exploited vulnerability and require synchronous contact, in addition to `security@ledgerproofhq.io`:

- **Signal**: Request Signal contact via email; we publish a Signal safety number after first contact
- **Phone**: Available on request via the email channel; we do not publish a static security phone number for spam-mitigation reasons
- **In-person hand-off**: Available in San Francisco, Brussels, or Amsterdam by prior arrangement

## SLA misses

*None to date. This section will be populated within 7 days of any miss, per § Response SLAs.*

## Published advisories

Foundation-issued security advisories are published at:

- `https://github.com/vsdawkins-creator/ledgerproof-eu/security/advisories` (GitHub Security Advisory format)
- `SECURITY-ADVISORIES.md` at the protocol repo root (mirror)
- This page, in the § Published advisories table below, with links to both above

| Advisory ID | Date | Severity | Component | Status |
|-------------|------|----------|-----------|--------|
| *No advisories issued to date.* | | | | |

## Cryptographic policy

- **Signing scheme**: Ed25519 (RFC 8032) for receipt signatures and Foundation governance events
- **Canonical encoding**: CBOR (RFC 8949 deterministic encoding subset)
- **Hash function for Merkle batching**: SHA-256
- **Bitcoin anchoring format**: OP_RETURN with `0x4C 0x50 0x52 0x31` ("LPR1") magic prefix followed by exactly 32 bytes of Merkle root
- **Key rotation cadence**: Interim Foundation signing key disclosed in `02-whitepaper/` and `04-lpr-spec/`. Multisig root-key ceremony scheduled for 15 August 2026 (Bitcoin-anchored); subsequent rotations on a documented cadence with anchored governance events.

A proposed change to any of the above is itself a governance event and is Bitcoin-anchored before deployment. The current interim Foundation signing public key is published in the protocol specification.

## Why we publish this page

EU AI Act Article 50 transparency obligations require evidence that survives the deployer's continued cooperation. A protocol whose security posture is opaque cannot deliver on that guarantee — a regulator, a journalist, or a data subject seeking accountability has to be able to evaluate the protocol's security claims independently of the Foundation's marketing.

This page exists so that:

1. A security researcher can disclose a vulnerability to us without needing to negotiate terms first
2. A regulator evaluating the protocol can read our actual SLAs and disclosure history rather than asking
3. A deployer choosing to integrate LedgerProof can see exactly how we will respond if something breaks
4. A downstream adapter maintainer knows what coordination to expect from us

If anything on this page is unclear, ambiguous, or contradicted by Foundation behavior, that itself is in-scope as a disclosure under § How to report — please report it.

---

*This policy is governed by the LedgerProof Foundation Charter (in formation, Delaware) and is subject to ratification by the Foundation Board on or before 31 August 2026. Until ratification, this policy operates as a public commitment of the founding executive director (Veronica S. Dawkins). Policy changes are Bitcoin-anchored as Foundation governance events of type `foundation_governance_event/v1` with `event_type = "security_policy_revision"`.*
