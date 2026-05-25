# LedgerProof EU Sprint — Status as of May 24, 2026 (Chunk 4 in flight)

## Where we are right now

**Rust extension complete + EU infrastructure provisioned + deploy in flight.**

| Phase | Status | Detail |
|---|---|---|
| Chunk 1: Merkle reform | ✅ Done | Commit `15819095` — 8/8 standalone tests |
| Chunk 2: EU AI Act 50 schema | ✅ Done | Commit `15e9cc49` — 11/11 standalone tests |
| Chunk 3: GDPR Article 17 soft-delete | ✅ Done | Commit `373dd0b6` — clean cargo check |
| Chunk 4: Deploy | 🔄 In flight | See below |

Branch: `feat/lpr-1.0-eu-spec-conformant` in `ledgerproof-platform`. Local-only,
not pushed to origin yet.

---

## Chunk 4 status — provisioned, deploy running

### Done
- ✅ `cargo build --release` verified clean on feature branch (20s, no errors)
- ✅ `fly.api-eu.toml` written (cost-minimal: single instance, shared-cpu-1x, 512 MB)
- ✅ Fly app `ledgerproof-api-eu` created
- ✅ EU Postgres `ledgerproof-db-eu` provisioned in `fra` (single node, shared-cpu-1x, 10 GB volume)
- ✅ 5 secrets staged on app:
  - `DATABASE_URL` (set to internal flycast URL of the EU Postgres)
  - `PUBLISHER_API_KEY_PEPPER` (random 32-byte hex)
  - `API_KEY_PEPPER` (random 32-byte hex)
  - `ADMIN_SECRET` (random 32-byte hex)
  - `CORS_ALLOWED_ORIGINS` (publish + verify + root domains)

### In flight
- 🔄 `fly deploy --config fly.api-eu.toml --remote-only --ha=false`
  - Building Docker image on Fly's remote builders
  - Will run `sqlx::migrate!` on first boot — applies all 5 migrations including `0005_gdpr_soft_delete.sql`
  - Expected wall-clock: 5-10 minutes (Rust compile in Docker)

### Cost ongoing once deploy is healthy
- Postgres (shared-cpu-1x, 10 GB):  ~$15-20/mo
- API machine (shared-cpu-1x, 512 MB, auto-stop on idle): ~$5-10/mo
- **Total: ~$25-35/mo** ✅ founder-approved

---

## Local secrets — all stored in `~/.ledgerproof-secrets/` (mode 0600)

| File | Contains |
|---|---|
| `operator_key.pem` | Ed25519 signing key for the future EU anchor worker (Phase 2). Public key: `d56a74aee71b8692183bc6d00cbc42babc9496eb84a887379e38f5134db87d87` |
| `api_key_salt.txt` | 32-byte hex salt (generated, not in current use) |
| `eu-postgres.txt` | Postgres credentials. **Rotate after deploy — password appeared in chat transcript.** |
| `eu-app-secrets.txt` | The three peppers + admin secret for ledgerproof-api-eu |

**⚠️ Back these four files up to 1Password before EU deploy serves real customers.**

---

## What comes next (after deploy success notification)

### Smoke-test plan
See `13-api-backend/EU-SMOKE-TEST-PLAN.md` — five tests covering health,
database reachability, anchor-list endpoint, admin-provision a test
publisher, and end-to-end receipt issuance.

### DNS step
See `13-api-backend/EU-DNS-PLAN.md` — exactly which records to add at
the DNS provider so `api-eu.ledgerproofhq.io` resolves to the new Fly app
(plus the `fly certs create` command to issue the TLS certificate).

---

## Architectural state across BOTH deployments

| System | Where | Purpose |
|---|---|---|
| `ledgerproof-api` (iad) | Existing US deployment | Legacy v0.x — serves the 3 historical anchors (May 6, 13, 18). Untouched by this sprint. |
| `ledgerproof-anchor` (iad) | Existing US worker | Daily Esplora-based broadcast. Untouched. |
| **`ledgerproof-api-eu` (fra)** | **New EU deployment** | **Spec-conformant LPR v1.0. RFC 6962 Merkle, 36-byte OP_RETURN, AI Act 50 schema, GDPR Article 17.** |
| ledgerproof-anchor-eu | Not deployed | Phase 2 — receipts queue PENDING until EU hot wallet is operationalized. |

---

*Last updated: May 24, 2026 — deploy in flight*
