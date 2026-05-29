# Incident Response Runbook

**Purpose:** The runbook for any production incident affecting receipt issuance, Bitcoin anchor commitment, verifier portal availability, or Audit-Ready Compliance Stamp PDF generation. Lives in the engineering repo so on-call has it in tab #1 during a page.

**Owner:** SRE (Day 90 hire) + Founder
**Last reviewed:** Day 30 (to be re-reviewed quarterly)

---

## Severity classification

| Severity | Definition | Response time | Page who |
|---|---|---|---|
| **SEV-0** | Customer cannot issue receipts globally OR verifier cannot verify ANY receipts | <5 min | Primary on-call + Founder + Spec Lead |
| **SEV-1** | Region-wide outage; OR Bitcoin anchor lag > 24h; OR Stamp PDF generation blocked across customers | <15 min | Primary on-call + Founder |
| **SEV-2** | Single-customer outage; OR latency SLO breach; OR partial feature failure | <30 min | Primary on-call |
| **SEV-3** | Degraded performance; customer-facing but recoverable | <2 hours | Primary on-call |
| **SEV-4** | Internal-only impact; no customer effect | Next business day | Primary on-call |

---

## On-call structure

**Through Day 60:** Founder is primary on-call 24/7. Senior Product Engineer backup.

**Day 60 onward:** Rotating on-call schedule:
- Primary: SRE (Day 90+) / Senior Product Engineer / Spec Lead
- Backup: Founder (always, while company size < 20)
- Escalation: Founder for any SEV-0 or SEV-1; mandatory ping

**Day 120 onward:** Founder removed from primary on-call rotation. Founder remains escalation for SEV-0 only.

**Day 180 onward:** Asia on-call coverage begins (Q2 2027 with Singapore hire). Pre-Asia: EU/US/UK shifts overlap with sleep gaps; SEV-0 wakes both primary and backup regardless of shift.

---

## When a page fires

### Step 1 — Acknowledge (within 5 min)
- Acknowledge the page in PagerDuty/Grafana OnCall
- Open incident channel in Slack: `#incident-<short-name>`
- Post in #eng-internal: "Acknowledging SEV-X for [brief description]"

### Step 2 — Assess (within 10 min)
- Pull status from:
  - status.ledgerproofhq.io public status page
  - Internal Grafana dashboards (operator, anchor lag, region health)
  - Recent deploys (anything in the last 4 hours?)
  - Bitcoin mempool conditions (mempool.space)
- Confirm or revise severity classification

### Step 3 — Contain (within 30 min for SEV-0/1)
- If recent deploy: roll back via release pipeline
- If region issue: route traffic away via SDK region resolver
- If Bitcoin anchor issue: see "Bitcoin anchor degraded mode" below
- If signing key issue: see "Key rotation under duress" below
- Communicate containment plan in incident Slack channel

### Step 4 — Communicate
- **SEV-0:** status page updated within 15 min; customer email within 30 min
- **SEV-1:** status page within 30 min; affected-customer email within 1 hour
- **SEV-2:** status page if customer-visible; direct outreach to affected customers
- **SEV-3+:** internal only unless customer asks

Templates live at `runbooks/communication-templates/`.

### Step 5 — Mitigate to resolution
- Continue containment + remediation actions
- Update status page every 30 min for SEV-0/1
- Update incident Slack every 15 min for SEV-0
- Do not declare resolution until measured metric confirms restoration

### Step 6 — Post-incident
- Postmortem within 5 business days for SEV-0/1; within 10 business days for SEV-2
- Public postmortem for SEV-0 (and SEV-1 if customer-visible) — published to status.ledgerproofhq.io
- Internal postmortem for SEV-2/3 — published to internal wiki
- Action items tracked in dedicated incident-followup label

---

## Specific scenario runbooks

### Bitcoin anchor lag > 24h

1. Check mempool.space fee estimates — congestion event?
2. Check operator's anchor commit queue depth
3. **Mitigation A — CPFP fee bump:** If parent anchor tx is stuck, queue a child tx with priority fee. Runbook entry: `runbooks/btc-cpfp-bump.md`
4. **Mitigation B — RBF on the anchor tx:** Bump fee on the original anchor tx using RBF. Runbook entry: `runbooks/btc-rbf-bump.md`
5. **Mitigation C — Multi-pool relay:** Re-submit to 3 pools. Runbook entry: `runbooks/btc-multi-pool-submit.md`
6. **Mitigation D — Degraded mode declaration:** If all mitigations fail within 6 hours, declare anchor degraded mode. Receipts continue to issue with `anchor_status: pending_extended` flag. Customer dashboard shows banner. Postmortem mandatory.

### Operator regional outage

1. Confirm region is down via 3 health checks (internal, customer-facing, third-party from outside)
2. SDK region resolver auto-routes; verify routing is working
3. Status page: "Region X experiencing degraded service; SDK is auto-routing to alternate region"
4. For customers pinned to `region="X-only"`: direct outreach via customer success; explain options
5. Fly.io support engaged immediately for SEV-1
6. Postmortem covers detection latency, routing effectiveness, customer impact

### Verifier portal outage

1. The verifier is CDN-fronted; CDN failure vs origin failure?
2. **CDN failure:** Switch to backup CDN (Cloudflare → Fastly fallback). Runbook: `runbooks/verifier-cdn-fallover.md`
3. **Origin failure:** Roll back to last known good deploy
4. **Critical:** Verifier outage doesn't invalidate receipts — they remain verifiable via the reference verifier and Bitcoin chain. Customer communication emphasizes this.

### Signing key compromise (suspected or confirmed)

This is a SEV-0 regardless of confirmation level.

1. Page Founder immediately
2. Pause new receipt issuance signing with the suspected key (operator returns 503 with explanation)
3. Generate new Ed25519 key pair (in HSM if available, otherwise software with witnesses)
4. Publish new DID document or eIDAS attestation with both keys (old + new) and a rotation timestamp
5. Resume issuance with new key
6. Publish public incident report within 24 hours
7. Notify all customers immediately; verifier portal flags receipts signed by suspected-compromised key with a warning
8. Forensics: determine compromise vector; full postmortem within 14 days

Receipts issued before the suspected compromise time remain valid (the Bitcoin anchor timestamps them). Receipts issued during the suspected compromise window are flagged but not invalidated.

### Database failover

1. Postgres health check failure triggers automatic promotion of read replica
2. Verify replication lag was acceptable at failover time
3. Confirm new primary is accepting writes
4. Confirm operator instances reconnected
5. Surface as SEV-1 if cross-region write quorum was lost; SEV-2 otherwise
6. Old primary investigated; root cause determined before re-introduction as replica

### PII discovery in production data

1. **Critical:** If any production data contains PII (email, name, SSN-like, etc.) — this means the schema rejection failed. SEV-0.
2. Pause new receipt issuance from the affected customer immediately
3. Identify how PII passed the SDK validator and the operator's defense-in-depth validation
4. Soft-delete the affected metadata
5. Notify affected customer within 4 hours
6. GDPR breach notification assessment by Founder + Counsel within 24 hours
7. Public postmortem if customer authorizes
8. Schema validator fix shipped same day; back-port to all SDK versions in support

---

## Tooling

| Tool | Use |
|---|---|
| Grafana OnCall (or PagerDuty) | Alerting and on-call rotation |
| Slack | Incident channels, real-time coordination |
| status.ledgerproofhq.io | Public status communication |
| Grafana dashboards | Internal observability |
| GitHub Issues with `incident` label | Tracking |
| GitHub Discussions | Post-incident discussion (where appropriate) |

---

## Communication principles

1. **Communicate even when there's no news.** Saying "investigating; next update in 30 min" beats silence.
2. **Be honest about what you know and what you don't.** "We don't yet know root cause; here is the symptom we observed" is better than speculation.
3. **Affected customers first; broader announcement second.** Email customers using the affected workflow before posting to social media.
4. **The Foundation publishes incident reports as receipts.** Dogfooding: the incident report is itself a LedgerProof Receipt, anchored, verifiable.
5. **No apologies in incident-window communication.** State facts and actions. Apologies belong in the postmortem if appropriate.

---

## Reviews

This runbook is reviewed:
- Quarterly (calendar reminder on Founder + SRE)
- After every SEV-0 or SEV-1
- When a new region is added
- When a new product surface (e.g., Stamp PDF, registry) goes GA
- When SRE on-call rotation changes

Updates are tracked in this file's commit history.

---

## What this runbook explicitly excludes

- Customer-side integration debugging (covered in customer support runbook)
- Security disclosure handling (covered in security disclosure policy)
- Foundation governance incidents (covered in Foundation governance docs)
- Personnel incidents (covered in HR policy)

If a page is genuinely outside this runbook's scope, the on-call's first action is to find the correct runbook owner and hand off cleanly.
