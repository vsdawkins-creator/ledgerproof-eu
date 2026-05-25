# EU Postgres Password Rotation

**Priority:** 🔴 CRITICAL — do this before any real customer uses the EU operator.
**Why:** The password appeared in chat during provisioning. Treat it as compromised.
**Time required:** ~5 minutes.
**Risk:** Zero downtime if the steps are followed in order (Fly restarts the app
automatically after `fly secrets set`).

---

## Step 1 — Connect to the EU Postgres cluster and rotate the password

Run this IN YOUR OWN TERMINAL (not through the agent):

```bash
# Open a psql session directly into the Postgres cluster via Fly
fly postgres connect --app ledgerproof-db-eu
```

Inside psql, run:

```sql
-- Replace <NEW_STRONG_PASSWORD> with a random 32-char password.
-- Suggested: openssl rand -base64 24   (run that in a separate terminal first)
ALTER ROLE postgres WITH PASSWORD '<NEW_STRONG_PASSWORD>';
\q
```

Generate the password first:
```bash
openssl rand -base64 24
# Example output: 7XkP2mQnR9vL4wYjF6cA8sBtEhNU3dVz
# Copy it — you'll use it in Step 1 and Step 2.
```

---

## Step 2 — Update the DATABASE_URL secret in the EU app

```bash
# The DATABASE_URL format is:
# postgres://postgres:<NEW_PASSWORD>@ledgerproof-db-eu.flycast:5432/postgres
#
# Replace <NEW_STRONG_PASSWORD> with the password from Step 1.

fly secrets set \
  DATABASE_URL="postgres://postgres:<NEW_STRONG_PASSWORD>@ledgerproof-db-eu.flycast:5432/postgres" \
  --app ledgerproof-api-eu
```

Fly will restart the app automatically. Watch:
```bash
fly status --app ledgerproof-api-eu
```

Wait for `running` status (~30 seconds).

---

## Step 3 — Verify the app is healthy

```bash
curl -i https://ledgerproof-api-eu.fly.dev/v1/health
```

Expected:
```json
{"db":"ok","service":"ledgerproof-api","status":"ok","version":"0.1.0"}
```

If `"db":"degraded"` → the DATABASE_URL was entered incorrectly. Re-run Step 2.

---

## Step 4 — Update your local secrets file

```bash
# Update ~/.ledgerproof-secrets/eu-postgres.txt with the new password.
# Then re-run your encrypted backup script:
~/.ledgerproof-secrets/backup-to-encrypted-dmg.sh
# Copy the updated .dmg to your 2 secure locations.
```

---

## Checklist

- [ ] Generated new password with `openssl rand -base64 24`
- [ ] `ALTER ROLE postgres WITH PASSWORD '...'` in psql
- [ ] `fly secrets set DATABASE_URL=...` — app restarted
- [ ] `curl /v1/health` returns `"db":"ok"`
- [ ] Updated `~/.ledgerproof-secrets/eu-postgres.txt`
- [ ] Re-ran encrypted DMG backup and stored in 2 secure locations

---

*The old password is now invalid. The chat log that exposed it cannot be changed,
but with the password rotated it has no attack surface.*
