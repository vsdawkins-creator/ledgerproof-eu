# LedgerProof API Backend — Deployment Runbook

**Target:** Fly.io EU deployment (`fra` / Frankfurt primary, `ams` / Amsterdam secondary)  
**Critical path deadline:** August 2, 2026 (EU AI Act Article 50 enforcement date)  
**Current state:** Code complete — needs Fly.io account setup, PostgreSQL provisioning, secrets, and first deploy.

---

## Prerequisites checklist

Before running any deploy command, confirm:

- [ ] Fly.io account created at fly.io
- [ ] `flyctl` installed: `curl -L https://fly.io/install.sh | sh`
- [ ] Authenticated: `fly auth login`
- [ ] DNS: `api.ledgerproofhq.io` and `api-eu.ledgerproofhq.io` CNAMEs ready to point at Fly.io
- [ ] Bitcoin node accessible (or Blockstream/QuickNode API credentials ready)
- [ ] Hot wallet funded with ≥ 0.001 BTC (for ~1000 anchor transactions)
- [ ] Hot wallet WIF private key available (never write it down; copy from secure key manager)

---

## Step 1 — Create the Fly.io app

```bash
# From the 13-api-backend/ directory
fly apps create ledgerproof-api-eu --org personal

# Confirm the app exists
fly apps list
```

---

## Step 2 — Provision the PostgreSQL database (EU region)

```bash
# Create a 2-node HA Postgres cluster in Frankfurt.
fly postgres create \
  --name ledgerproof-db-eu \
  --region fra \
  --initial-cluster-size 2 \
  --vm-size shared-cpu-2x \
  --volume-size 50

# Attach the database to the API app (sets DATABASE_URL automatically).
fly postgres attach ledgerproof-db-eu \
  --app ledgerproof-api-eu
```

This sets `DATABASE_URL` as a secret on `ledgerproof-api-eu` automatically.

---

## Step 3 — Generate the operator signing key

```bash
# Run this on a secure machine (not CI).
# The key will be stored on the Fly.io persistent volume at /data/operator_key.pem.
# After generating, we upload it to the Fly volume before first deploy.

python -m lpr_api.keygen --output /tmp/operator_key.pem

# Output will include the public key hex — SAVE IT.
# You will need it to register with the LedgerProof Foundation.

# Copy the key to the Fly.io volume (after the app and volume are created).
# See Step 5 for volume setup.
```

**CRITICAL:** Back up `/tmp/operator_key.pem` to offline encrypted storage (1Password, hardware key).  
If lost, all past anchors cannot be attributed to this operator.

---

## Step 4 — Set Fly.io secrets

```bash
# Set all required secrets at once.
# Replace <values> with your actual credentials.
# These are NEVER stored in code or config files.

fly secrets set \
  --app ledgerproof-api-eu \
  BITCOIN_HOT_WALLET_WIF="<your_WIF_private_key>" \
  API_KEY_SALT="<64_random_bytes_hex>" \
  BTCD_RPC_HOST="<bitcoin_rpc_host>" \
  BTCD_RPC_USER="<bitcoin_rpc_user>" \
  BTCD_RPC_PASS="<bitcoin_rpc_password>"

# Verify secrets are set (values are never shown, only names).
fly secrets list --app ledgerproof-api-eu
```

Generate a strong API_KEY_SALT:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## Step 5 — Create persistent volume and upload signing key

```bash
# Create the volume for the signing key and receipt WAL.
fly volumes create ledgerproof_eu_data \
  --app ledgerproof-api-eu \
  --region fra \
  --size 10

# Upload the signing key to the volume.
# This uses fly sftp (SSH file transfer to the running container).
# First, do a one-off machine start to access the volume:
fly machine run \
  --app ledgerproof-api-eu \
  --volume ledgerproof_eu_data:/data \
  python:3.11-slim \
  --command "sleep 300"

# Then in another terminal, copy the key:
fly sftp get /data/operator_key.pem /tmp/from_fly_key.pem  # sanity check (should 404)
fly sftp shell  # then: put /tmp/operator_key.pem /data/operator_key.pem

# Or use fly machine exec for a one-liner after first deploy:
# fly ssh console --app ledgerproof-api-eu
# Then: cat > /data/operator_key.pem (paste PEM, ctrl-D)
```

---

## Step 6 — Run database migrations

```bash
# Alembic migrations run automatically on deploy via release_command in fly-eu.toml.
# But you can also run them manually:

fly ssh console --app ledgerproof-api-eu
# Inside the container:
DATABASE_URL=$DATABASE_URL python -m alembic upgrade head
exit
```

---

## Step 7 — Deploy

```bash
# From the 13-api-backend/ directory.
fly deploy \
  --config ../12-eu-compliance/05-FLY-EU-DEPLOYMENT.toml \
  --dockerfile Dockerfile.api

# Watch the deployment logs.
fly logs --app ledgerproof-api-eu
```

Expected output on successful deploy:
```
INFO:lpr.signing:Signing key loaded. Public key: <hex>...
INFO:lpr.database:PostgreSQL pool initialized (min=2, max=20)
INFO:lpr.anchor_worker:Anchor worker started (interval=86400s / 24.0h)
INFO:uvicorn:Application startup complete.
```

---

## Step 8 — Configure DNS

```bash
# Get the Fly.io allocated IP for the app.
fly ips list --app ledgerproof-api-eu

# In your DNS provider (Cloudflare, Route53, etc.):
# Add: api-eu.ledgerproofhq.io CNAME ledgerproof-api-eu.fly.dev
# Add: api.ledgerproofhq.io    CNAME ledgerproof-api-eu.fly.dev (or geo-route to US for non-EU)
```

---

## Step 9 — Smoke test

```bash
# Health check.
curl https://api-eu.ledgerproofhq.io/health | python3 -m json.tool

# Operator identity.
curl https://api-eu.ledgerproofhq.io/.well-known/lpr-operator | python3 -m json.tool

# Issue a test receipt (requires a valid API key).
# First, create an API key in the database:
fly ssh console --app ledgerproof-api-eu
python3 -c "
import asyncio, hashlib, hmac, os, uuid
salt = os.environ['API_KEY_SALT']
raw_key = 'lpr_' + uuid.uuid4().hex
key_hash = hmac.new(salt.encode(), raw_key.encode(), hashlib.sha256).hexdigest()
print(f'Raw key: {raw_key}')
print(f'Key hash: {key_hash}')
# INSERT INTO api_keys (key_id, key_hash, name, tier) VALUES ('<uuid>', '<hash>', 'founder', 'internal');
"
# Then run the INSERT in psql (fly postgres connect --app ledgerproof-db-eu).

# Test receipt issuance.
curl -X POST https://api-eu.ledgerproofhq.io/receipts \
  -H "Authorization: Bearer <your_api_key>" \
  -H "Content-Type: application/json" \
  -d '{
    "content_hash": "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3",
    "content_type": "text/plain",
    "content_bytes": 11,
    "actor_type": "AI_MODEL",
    "actor_id": "openai/gpt-4o/2024-11-20",
    "actor_assertion": "Smoke test receipt"
  }' | python3 -m json.tool

# Expected: HTTP 201 with receipt_id and anchor_status: PENDING
```

---

## Step 10 — Register with the LedgerProof Foundation

```bash
# Email operators@ledgerproofhq.io with:
# - Your /.well-known/lpr-operator URL: https://api-eu.ledgerproofhq.io/.well-known/lpr-operator
# - Your Bitcoin address (for anchor attribution)
# - Organization name: LedgerProof Foundation (EU Calendar)
# - Country: DE
# - Ed25519 public key: <from Step 3 output>
```

---

## Monitoring

```bash
# Metrics (Prometheus format) on port 9090.
fly proxy 9090 --app ledgerproof-api-eu

# Then in another terminal:
curl http://localhost:9090/metrics | grep lpr_

# Key metrics to watch:
# lpr_anchor_age_hours > 26 → anchor overdue (alert)
# lpr_pending_receipts > 100000 → queue backing up
# lpr_btc_balance_sats < 10000 → fund the hot wallet
# lpr_db_lag_seconds > 5 → database replication lag

# Live logs:
fly logs --app ledgerproof-api-eu -f

# Check anchor worker:
fly logs --app ledgerproof-api-eu | grep "anchor"
```

---

## Rollback

```bash
# List recent deployments.
fly releases --app ledgerproof-api-eu

# Roll back to a previous version.
fly deploy --image <previous_image_ref> --app ledgerproof-api-eu
```

---

## EU compliance checklist (before August 2, 2026)

- [ ] API deployed in Frankfurt (`fra` region) ✅ (configured in fly-eu.toml)
- [ ] TLS 1.3 enforced ✅ (Fly.io default)
- [ ] `GDPR_MODE=true` set ✅ (configured in fly-eu.toml)
- [ ] `EU_AI_ACT_50_ENABLED=true` set ✅ (configured in fly-eu.toml)
- [ ] DPA template reviewed by legal counsel and executed with first EU customer
- [ ] Data retention policy documented (25-year default is set in schema)
- [ ] Incident response procedure in place (notify security@ledgerproofhq.io within 24h)
- [ ] First EU enterprise customer pilot anchoring receipts before enforcement date
- [ ] At least one independent EU calendar operator registered

---

## Security hardening (post-launch, before institutional onboarding)

- [ ] Rate limiting: add Redis-backed rate limiter per API key (current: DB-based, sufficient for launch)
- [ ] mTLS for enterprise API keys (per-tenant client certificates)
- [ ] HSM integration for operator signing key (Fly.io → AWS CloudHSM or Thales)
- [ ] Annual Ed25519 key rotation procedure (as required for EU operators per spec §5.4)
- [ ] SOC 2 Type II audit engagement (target: Q1 2027)
- [ ] GDPR DPO appointment if processing volume exceeds threshold

---

*LedgerProof Foundation · API Backend Deployment Runbook · May 2026*
