# LedgerProof EU API — Smoke Test Plan

**Target:** `ledgerproof-api-eu` (Fly, region `fra`, hostname `ledgerproof-api-eu.fly.dev` until DNS is wired)
**Purpose:** confirm the EU API is healthy, schema migrations applied, and end-to-end receipt issuance works before any real customer traffic.

---

## Test 1 — Basic health (no auth)

```bash
curl -i https://ledgerproof-api-eu.fly.dev/v1/health
```

**Expected:**
- HTTP 200
- Body: `{"db":"ok","service":"ledgerproof-api","status":"ok","version":"0.1.0"}`
- Headers include `server: Fly/...` and a non-empty `fly-request-id`

**Pass criterion:** `"db":"ok"` confirms the EU Postgres is reachable from the EU app via flycast.

**If fail:**
- 404 → router not started; check `fly logs --app ledgerproof-api-eu`
- 503 or `"db":"degraded"` → DATABASE_URL secret wrong or Postgres machine asleep
- timeout → app machine not running; `fly status --app ledgerproof-api-eu`

---

## Test 2 — Anchor-list endpoint (no auth, exercises read path)

```bash
curl -s https://ledgerproof-api-eu.fly.dev/v1/anchors | python3 -m json.tool
```

**Expected:**
- HTTP 200
- Body: `{"anchors":[]}`  (empty array — no anchors yet on EU operator)

**Pass criterion:** confirms `anchors` table exists (migrations applied).

---

## Test 3 — Schema migration audit

```bash
# Connect to EU Postgres via Fly proxy
fly proxy 15432:5432 --app ledgerproof-db-eu &
sleep 2
PGPASSWORD='lVsM03xlM99aS0w' psql -h 127.0.0.1 -p 15432 -U postgres -c "\\d entries"
PGPASSWORD='lVsM03xlM99aS0w' psql -h 127.0.0.1 -p 15432 -U postgres -c "SELECT version FROM _sqlx_migrations ORDER BY version;"
kill %1
```

**Expected `\d entries`:**
- `content`              JSONB,        NULL OK
- `entry_json_canonical` TEXT,         NULL OK
- `deleted_at`           TIMESTAMPTZ,  NULL OK
- `deleted_reason`       TEXT,         NULL OK
- Index `idx_entries_deleted_at` on `deleted_at WHERE deleted_at IS NOT NULL`

**Expected migrations:** rows `1, 2, 3, 4, 5` — confirms `0005_gdpr_soft_delete.sql` ran on first deploy.

---

## Test 4 — Admin-provision a test publisher (auth + write path)

```bash
# Use ADMIN_SECRET from ~/.ledgerproof-secrets/eu-app-secrets.txt
ADMIN_SECRET=$(grep '^ADMIN_SECRET' ~/.ledgerproof-secrets/eu-app-secrets.txt | awk '{print $3}')

curl -s -X POST https://ledgerproof-api-eu.fly.dev/v1/admin/provision \
  -H "Authorization: Bearer $ADMIN_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "publisher_id":   "eu-smoke-test-001",
    "display_name":   "EU Smoke Test Publisher",
    "contact_email":  "founder@ledgerproofhq.io"
  }'
```

**Expected:**
- HTTP 201
- Body contains `api_key` (raw — shown once)

**Save the returned `api_key`** — needed for Test 5.

**Pass criterion:** confirms the admin route works, the `publishers` table accepts inserts, and HMAC key hashing functions correctly.

---

## Test 5 — End-to-end EU AI Act Article 50 receipt issuance

```bash
# Use the api_key from Test 4
TEST_API_KEY="lpr_..."   # from Test 4

# 1. Register a publisher signing key (key ceremony)
#    For smoke test, generate a test Ed25519 keypair locally:
python3 << 'EOF'
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
import base64

sk = Ed25519PrivateKey.generate()
pk = sk.public_key().public_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PublicFormat.Raw,
)
print("SIGNING_KEY_BYTES_HEX:", sk.private_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PrivateFormat.Raw,
    encryption_algorithm=serialization.NoEncryption(),
).hex())
print("VERIFYING_KEY_B64:", base64.b64encode(pk).decode())
EOF
```

**Save VERIFYING_KEY_B64 and SIGNING_KEY_BYTES_HEX.**

```bash
# 2. Register the public key on the operator
curl -s -X POST https://ledgerproof-api-eu.fly.dev/v1/keys \
  -H "X-Api-Key: $TEST_API_KEY" \
  -H "X-Publisher-Id: eu-smoke-test-001" \
  -H "Content-Type: application/json" \
  -d "{
    \"key_id\":           \"smoke-key-001\",
    \"verifying_key_b64\": \"<VERIFYING_KEY_B64>\",
    \"effective_from_sequence\": 0
  }"
```

**Expected:** HTTP 201

```bash
# 3. Compute and submit the first entry — an EU AI Act 50 receipt
#    See 13-api-backend/eu-ai-act-50-test-receipt.py for the full
#    end-to-end script that builds the canonical JSON, signs it, and
#    POSTs to /v1/publish.
python3 13-api-backend/eu-ai-act-50-test-receipt.py \
  --api-base https://ledgerproof-api-eu.fly.dev \
  --api-key $TEST_API_KEY \
  --publisher-id eu-smoke-test-001 \
  --key-id smoke-key-001 \
  --signing-key-hex <SIGNING_KEY_BYTES_HEX>
```

**Expected output:**
```
{
  "sequence":     0,
  "entry_hash":   "<64-char hex>",
  "receipt_id":   0
}
```

**Pass criterion:** the receipt is accepted, the chain genesis entry exists with `content_type = "ai/article-50/v1"`, and the `eu_ai_act_50` schema passed server-side validation.

---

## Test 6 — Verify the receipt readable via public GET

```bash
curl -s https://ledgerproof-api-eu.fly.dev/v1/entries/0 | python3 -m json.tool
```

**Expected:**
- HTTP 200
- Body contains the full entry with `content_type: "ai/article-50/v1"` and the populated `content` payload (ai_system_id, deployer_id, etc.)
- `deleted_at: null`

---

## Test 7 — GDPR Article 17 erasure

```bash
curl -i -X DELETE https://ledgerproof-api-eu.fly.dev/v1/entries/0 \
  -H "X-Api-Key: $TEST_API_KEY" \
  -H "X-Publisher-Id: eu-smoke-test-001"
```

**Expected:** HTTP 204 No Content

```bash
# Re-read after erasure
curl -s https://ledgerproof-api-eu.fly.dev/v1/entries/0 | python3 -m json.tool
```

**Expected:**
- `content: null`
- `entry_json_canonical: null`
- `deleted_at: "<timestamp>"`
- `deleted_reason: "GDPR Article 17 erasure request"`
- `entry_hash`, `prev_hash`, `signature` STILL PRESENT (chain intact)

**Pass criterion:** PII columns nulled, chain identity preserved.

---

## Pass-fail summary

| Test | Validates |
|---|---|
| 1 | API process running, DB reachable |
| 2 | Migrations applied (anchors table exists) |
| 3 | Schema migration 0005 applied correctly |
| 4 | Admin route + publisher creation |
| 5 | End-to-end EU AI Act 50 receipt issuance + schema validation hook |
| 6 | Public read of structured Article 50 content |
| 7 | GDPR Article 17 erasure with chain preservation |

**Production-ready criterion:** all 7 pass.

**Demo-ready criterion (Wednesday TVP):** tests 1-2 + 4-6 pass. Test 7 nice-to-have.

---

*To run all tests in sequence after deploy:*
```bash
cd ~/Documents/LedgerProof-Launch-July6/13-api-backend
./run-eu-smoke-tests.sh
```
