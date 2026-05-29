# Operator Load Test Plan — 10M Receipts/Day

**Purpose:** Prove the EU operator handles 10x the current production load without SLO degradation. Article 50 enforcement on August 2 may produce spikes of 5–8x normal volume from a single customer in the first 72 hours; the operator must absorb that as routine.

**Owner:** Founder
**Test window:** July 8–22 (two-week window; three full runs)
**SLOs being validated:**
- Receipt issuance p99 ≤ 200ms (Schedule B target)
- Receipt acceptance success rate ≥ 99.95%
- Bitcoin anchor commitment within 24h ≥ 99% (SLO)
- Operator API availability ≥ 99.5% (SLO target; 99.9% aspirational)

---

## Test workloads

### W1 — Baseline (current production shape)
- 100K receipts/day
- Constant rate
- Single tenant
- Validates the test harness itself

### W2 — Steady scale-up (target shape)
- 10M receipts/day = ~116 receipts/second sustained
- 10 simulated tenants, weighted Zipf distribution (top tenant ~60% of load)
- 24-hour continuous run
- Validates sustained throughput

### W3 — Burst (worst-case shape)
- 100M receipts in 4 hours (~7K receipts/second sustained)
- Single tenant
- Validates surge handling and Bitcoin anchor batching under load

### W4 — Failure injection (resilience shape)
- 1M receipts/hour
- Inject failures every 10 minutes: kill operator pod, kill Bitcoin RPC, kill database read replica
- Validates retry, queue, and recovery semantics

### W5 — Multi-region readiness preview (Day 60 prep)
- Same as W2, but with traffic split 70/30 across two operator regions
- US operator not yet GA; runs in shadow mode
- Validates that traffic routing works without changing receipt semantics

---

## Test harness

**Tooling:** k6 for HTTP load; custom Python harness for batch endpoint; Bitcoin regtest network for anchor simulation; chaos-mesh or manual chaos for failure injection.

**Harness lives at:** `ledgerproof-platform/loadtests/`

**Data fidelity:**
- Real receipt schemas
- Real cryptographic operations (Ed25519 signing per receipt)
- Synthetic but realistic payload sizes (5–15 KB receipt bodies typical)
- Bitcoin anchoring against a private regtest network with simulated mempool latency

**No customer data ever used in load tests.** All payloads generated from synthetic fixtures.

---

## Pass criteria per workload

| Workload | Throughput SLO | Latency p99 | Availability | Anchor SLO |
|---|---|---|---|---|
| W1 — Baseline | n/a | ≤200ms | ≥99.5% | ≥99% within 24h |
| W2 — Steady | 116 RPS sustained for 24h | ≤200ms | ≥99.5% | ≥99% within 24h |
| W3 — Burst | 7K RPS for 4h | ≤500ms acceptable | ≥99% during burst | ≥95% within 24h (acceptable degradation) |
| W4 — Failures | 1M/hour with chaos | recovery within 5 min of each injection | ≥99% over the run | ≥99% within 24h |
| W5 — Multi-region preview | 116 RPS split 70/30 | ≤200ms | ≥99.5% | ≥99% within 24h |

**Any failure to meet SLO triggers a remediation cycle before Day 30.**

---

## Capacity model

| Resource | Current allocation | Day 30 target | Day 60 target |
|---|---|---|---|
| Fly.io app instances (EU) | 2 × shared-cpu-1x | 4 × shared-cpu-4x | 6 × shared-cpu-4x |
| Database (Postgres on Fly) | Single | Primary + 1 read replica | Primary + 2 read replicas |
| Object storage for receipts | Fly volumes | S3-compatible (Tigris) | Same |
| Bitcoin RPC | 2 endpoints (failover) | 4 endpoints + relay | Same |
| CDN for verifier portal | Cloudflare | Cloudflare + R2 origin | Same |

**Cost model:** ~$2K/month at Day 30 target; ~$4K/month at Day 60 target. Documented in operator cost-per-receipt review.

---

## Bitcoin anchor strategy under load

The current anchor strategy is one Merkle root per ~10-minute window. Under W3 (7K RPS burst), one window contains ~4.2M receipts. That is fine — the Merkle root size is constant (32 bytes), and the OP_RETURN payload is fixed at 36 bytes regardless of leaf count.

**Mempool risk:** During a Bitcoin congestion event, anchor commitment can lag the 24-hour SLO. Mitigations in priority order:

1. **CPFP fee bumping.** Operator monitors fee market; if a parent anchor tx is stuck, an unrelated child tx with high fee pulls it through (Child-Pays-For-Parent).
2. **RBF on the anchor tx.** Operator marks anchor txs as RBF-eligible and bumps fee at the 6-hour mark if not confirmed.
3. **Multi-pool relay.** Operator submits anchor tx to three pools (mempool.space + two others) simultaneously.
4. **Documented degraded-mode operation.** If anchor lag exceeds 24h despite mitigations, operator continues issuing receipts but flags them in the API response with `anchor_lag_warning`. Customer SDK surfaces the warning.

**Customer-facing transparency:** Anchor lag is exposed on the public dashboard and in every receipt's `anchor_status` field. No hidden state.

---

## Observability instrumentation pre-test

| Signal | Owner | Status |
|---|---|---|
| Per-endpoint p50/p95/p99 latency | Operator | required before W2 |
| Per-tenant request rate | Operator | required before W2 |
| Bitcoin anchor lag histogram | Operator | required before W3 |
| Database connection pool utilization | Operator | required before W2 |
| Cryptographic operation latency (Ed25519 sign, SHA-256 hash) | Operator | required before W2 |
| Queue depth (operator-side batch queue) | Operator | required before W3 |
| Error rate by error class | Operator | required before W2 |
| SDK-side fallback queue depth (if SDK 1.1 deployed by tenants) | SDK | required for W4 |

---

## Pre-flight (must close before W1 begins)

- [ ] Test harness in `ledgerproof-platform/loadtests/` runs locally against staging
- [ ] Staging operator provisioned with same topology as production
- [ ] Bitcoin regtest network configured for anchor simulation
- [ ] Synthetic fixture data generated (1 TB)
- [ ] Cost budget for staging environment approved (~$3K total for two-week window)
- [ ] Founder + product engineer paired on harness debugging session

## Post-test deliverables

- [ ] Per-workload SLO report (one page per workload)
- [ ] Aggregated capacity recommendations
- [ ] Cost-per-receipt model updated
- [ ] Capacity dashboard added to internal Grafana
- [ ] Bitcoin anchor degraded-mode runbook updated
- [ ] CHANGELOG entry on operator release notes
- [ ] Customer-facing capacity statement: "EU operator validated to 10M receipts/day with documented SLOs at all observation points"

---

## Stop conditions during test

Halt the test immediately if:

1. Production EU operator availability drops below 99% (test traffic somehow leaking into prod)
2. Any test traffic anchors to Bitcoin mainnet (must only anchor to regtest)
3. Any test produces a receipt containing PII (validates schema rejection failure)
4. Test cost exceeds $5K total budget without founder approval to continue
5. Test harness itself becomes the bottleneck (limits the validity of throughput claims)

The first three are P0 incidents requiring a postmortem before the next test run.
