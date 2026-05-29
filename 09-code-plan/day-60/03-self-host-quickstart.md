# Self-Hosted Operator Quickstart — Reference Implementation

**Purpose:** Publish a Foundation-maintained, Apache 2.0-licensed reference operator that any customer can deploy in their own infrastructure to issue LedgerProof Receipts without depending on LedgerProof Inc. This is the **structural moat** of the open-protocol thesis: customers can leave us without abandoning the protocol.

**Owner:** Spec lead + Founder
**Repo:** `github.com/ledgerproof/operator-ref`
**Target release:** Day 60 (alpha) → Day 90 (1.0 stable)

---

## What "reference implementation" means

The reference operator is **functionally equivalent** to the LedgerProof Inc. commercial operator at the protocol layer. A receipt issued by the reference operator verifies under the same verifier as a receipt issued by LedgerProof Inc. There is no protocol-level distinction.

What the reference operator is NOT:
- A turnkey commercial product
- Operationally hardened to the same SLO LedgerProof Inc. holds
- Supported by LedgerProof Inc. business hours
- Pre-integrated with billing, customer success, Big-4 partnerships

Customers who self-host operate their own SRE function.

---

## The 30-minute self-host story

```bash
# Prerequisites: Docker, a Bitcoin RPC endpoint, a Postgres instance.
git clone https://github.com/ledgerproof/operator-ref
cd operator-ref
cp .env.example .env
# Edit .env: BITCOIN_RPC_URL, POSTGRES_URL, OPERATOR_SIGNING_KEY (Ed25519)
docker compose up -d
curl -X POST http://localhost:8080/v1/receipts \
  -H "Content-Type: application/json" \
  -d '{"output_hash": "abc...", "issuer_did": "did:web:example.com", ...}'
# → returns receipt_id
```

A customer with a working Docker host and a Bitcoin RPC endpoint goes from clone to first receipt in under 30 minutes. The quickstart documentation is tested in CI on each release.

---

## Repository structure

```
operator-ref/
├── README.md                      ← 30-minute quickstart
├── LICENSE                        ← Apache 2.0
├── CONTRIBUTING.md                ← CLA required for protocol-affecting PRs
├── docker-compose.yml             ← One-command deploy
├── helm/                          ← Kubernetes Helm chart
├── terraform/                     ← Terraform modules for AWS / Azure / GCP
├── cmd/
│   └── operator/                  ← Go entry point
├── internal/
│   ├── receipt/                   ← Receipt schema + signing
│   ├── anchor/                    ← Bitcoin anchoring
│   ├── merkle/                    ← RFC 6962 Merkle tree
│   ├── storage/                   ← Postgres + object storage
│   ├── api/                       ← HTTP server
│   └── observability/             ← Prometheus + OpenTelemetry
├── docs/
│   ├── architecture.md
│   ├── operations.md
│   ├── upgrade.md
│   └── security.md
├── examples/
│   ├── docker-compose-minimal/
│   ├── kubernetes-eks/
│   ├── kubernetes-aks/
│   └── kubernetes-gke/
└── tests/
    ├── conformance/               ← Run against any LPR operator implementation
    └── load/
```

**Language choice: Go.** Easier deployment story (single binary), strong cryptographic library ecosystem, predictable resource profile under load. The commercial LedgerProof Inc. operator is currently in Rust; the reference impl in Go demonstrates protocol portability across languages.

---

## Conformance test suite

The conformance suite is the regression that proves the reference operator and the LedgerProof Inc. commercial operator produce protocol-identical receipts. Lives in `operator-ref/tests/conformance/`. Any operator implementation (LedgerProof Inc., self-hosted, or future third-party) runs the same suite and must pass.

Conformance categories:
1. **Receipt issuance** — given the same input, produce a byte-identical signed receipt
2. **Merkle tree construction** — given the same receipt set, produce the same Merkle root
3. **Bitcoin anchor format** — OP_RETURN bytes match `"LPR1" || merkle_root_32`
4. **Verifier compatibility** — receipts verify under reference verifier
5. **Schema rejection** — PII is rejected at the boundary (defense-in-depth)
6. **Soft-delete semantics** — erasure requests produce correct attestations
7. **Profile resolution** — known profiles produce expected field-set validations

Suite is part of every operator-ref CI run. The commercial operator runs the same suite in its own CI. A divergence between the two operators on the conformance suite is a P0 protocol bug.

---

## What customers get with the reference operator

| Capability | Reference operator | Commercial LedgerProof Inc. operator |
|---|---|---|
| Receipt issuance | ✓ | ✓ |
| Bitcoin anchoring | ✓ (uses customer's RPC) | ✓ (operator-managed) |
| Merkle tree construction | ✓ | ✓ |
| Public verifier (verify.ledgerproofhq.io) | ✓ (receipts verifiable there) | ✓ |
| Soft-delete | ✓ | ✓ |
| Profile resolution | ✓ | ✓ |
| Audit-Ready Compliance Stamp PDF generation | ✓ (reference template) | ✓ (production template + customer co-branding) |
| Multi-region failover | Customer builds | ✓ (EU + US + UK) |
| 24/7 ops + SLO | Customer's SRE | ✓ (99.9% target) |
| Big-4 partner co-branding | — | ✓ |
| Customer support | Community (GitHub issues) | ✓ (per-tier SLOs) |
| Billing infrastructure | — | ✓ |
| Foundation membership fees | $25K/year (operator membership) | Included in commercial pricing |

---

## Foundation membership for operators

Any organization running the reference operator (or their own protocol-conformant operator) is eligible for Foundation operator membership at $25K/year. Membership confers:

- Voting seat on the Foundation Advisory Council
- Right to issue receipts under the `lpr.*` profile namespace
- Inclusion in the public registry of authorized operators
- Right to be referenced as an operator in customer procurement conversations
- Access to the conformance suite + early-look at upcoming spec revisions

Membership is not required to run the operator (the protocol is open). Membership is required to be listed in the canonical operator registry.

---

## What this unlocks commercially

The self-host story is what closes Big-4 partnership LOIs and large FSI deals. The conversation pattern:

> **General Counsel:** "What happens if LedgerProof Inc. fails?"
> **Sales:** "Two paths. One: another Foundation member operator. Two: you self-host the open reference implementation. We'll help you do either."

Without a working self-host story, the GC's question has no good answer. With one, the question becomes a sales asset.

We expect 5–10% of customers to actually self-host. The 90% who do not still buy on the strength of the option.

---

## Release process

| Date | Action |
|---|---|
| Day 50 | First public commit on `operator-ref`; private cleanup before this |
| Day 53 | Conformance suite runs against commercial operator in CI |
| Day 55 | docker-compose and quickstart docs published |
| Day 58 | Helm chart and Terraform modules published |
| Day 60 | Alpha release announced; 3 design partners invited to deploy |
| Day 75 | Beta release with design partner feedback incorporated |
| Day 90 | 1.0 stable release; public announcement; first non-LedgerProof Foundation member operator declares intent |

---

## Open questions

1. **CLA structure.** Single CLA for the Foundation, or per-repo? **Recommend Foundation-wide CLA modeled on Apache ICLA.**
2. **Code attribution.** How prominently do we acknowledge that the commercial operator and the reference operator share architecture? **Recommend explicit acknowledgment in README — transparency is the asset.**
3. **Cryptographic primitives library.** Do we maintain our own or depend on standard libraries? **Recommend depend (Go crypto/ed25519, golang.org/x/crypto). Our own bug surface should be zero on primitives.**
4. **Support obligation.** Does Foundation provide bug-fix support to self-hosters, or is it community-supported only? **Recommend community-supported with Foundation maintainers responding to spec-affecting issues within 7 days. Anything else is on the customer.**
5. **Compliance attestations for self-hosters.** Can a self-hoster get a SOC 2 attestation that applies to their deployment? **No — SOC 2 covers operational controls, not protocol implementation. We document this clearly.**
