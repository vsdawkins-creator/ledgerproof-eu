# LedgerProof EU API — DNS Wire-Up Plan

**Purpose:** point `api-eu.ledgerproofhq.io` at the new Fly app and issue a TLS certificate, without touching the existing `api.ledgerproofhq.io` DNS that serves the legacy v0.x system.

---

## Step 1 — Get the EU app's network addresses

```bash
fly ips list --app ledgerproof-api-eu
```

**Expected output** (example — your actual addresses will differ):
```
VERSION │ IP                          │ TYPE                       │ REGION
v6      │ 2a09:8280:1::...            │ public ingress (dedicated) │ global
v4      │ 66.241.x.x                  │ public ingress (shared)    │
```

The IPv6 address is dedicated to your app. The IPv4 is a shared Fly ingress (multiple apps; routed by SNI / Host header).

For a CNAME-style hookup we **don't need the raw IPs** — we just need the Fly hostname: `ledgerproof-api-eu.fly.dev`.

---

## Step 2 — Add DNS records at your DNS provider

`ledgerproofhq.io` DNS is currently hosted at... (need to confirm — could be Cloudflare, Route53, Namecheap, etc. Check by running `dig +short NS ledgerproofhq.io` from terminal).

Add ONE new record. **Do not modify any existing records.**

| Type | Name | Value | TTL |
|---|---|---|---|
| CNAME | `api-eu` | `ledgerproof-api-eu.fly.dev.` | 300 (5 min) |

A CNAME is the simplest path because Fly will resolve to the right IPv4/IPv6 endpoint based on the client.

**Alternative if your DNS provider doesn't support CNAME at the apex but does for subdomains** (it does, since this is a subdomain): the CNAME approach above works.

**Alternative if you prefer A/AAAA records** (slightly more brittle, requires updating IPs if Fly rotates them):

| Type | Name | Value | TTL |
|---|---|---|---|
| A | `api-eu` | `<the IPv4 from fly ips list>` | 300 |
| AAAA | `api-eu` | `<the IPv6 from fly ips list>` | 300 |

---

## Step 3 — Tell Fly to issue a TLS certificate

```bash
fly certs create --app ledgerproof-api-eu api-eu.ledgerproofhq.io
```

Fly will use ACME (Let's Encrypt) to provision the certificate. Behind the scenes Fly performs the DNS-01 challenge automatically because the CNAME points to its infrastructure. Cert issuance typically takes 1-5 minutes once DNS propagation completes.

**Monitor cert status:**
```bash
fly certs show api-eu.ledgerproofhq.io --app ledgerproof-api-eu
```

Wait for `STATUS: Issued`.

---

## Step 4 — Confirm DNS propagation

```bash
# Check from the public internet
dig +short api-eu.ledgerproofhq.io
# Should return: ledgerproof-api-eu.fly.dev.  (and then resolve to a Fly IP)

# Sanity check resolution path
curl -sI https://api-eu.ledgerproofhq.io/v1/health | head -10
```

**Expected:**
- HTTP/2 200
- `server: Fly/...`
- TLS certificate issuer: `Let's Encrypt`

---

## Step 5 — Verify TLS cert chain

```bash
echo | openssl s_client -servername api-eu.ledgerproofhq.io -connect api-eu.ledgerproofhq.io:443 2>/dev/null | openssl x509 -noout -subject -issuer -dates
```

**Expected:**
- Subject: `CN=api-eu.ledgerproofhq.io`
- Issuer: Let's Encrypt R10/R11 (or whatever's current)
- Validity: ~90 days forward
- Fly auto-renews ~30 days before expiry

---

## Step 6 — Add origin to publish.ledgerproofhq.io / verify.ledgerproofhq.io

The publisher web app (`publish.ledgerproofhq.io`) currently hardcodes `api.ledgerproofhq.io` as its API origin. For EU customers to use the EU operator, the publisher app needs to recognize `api-eu.ledgerproofhq.io` as an alternate.

Two options:

**A. Region-aware client config (recommended)** — the publisher app reads a region selector from the URL/UI and routes API calls accordingly:
```js
const API_BASE = window.location.search.includes("region=eu")
  ? "https://api-eu.ledgerproofhq.io"
  : "https://api.ledgerproofhq.io";
```

**B. Standalone EU publisher domain** — separate frontend at `publish-eu.ledgerproofhq.io` that hardcodes the EU API. Cleaner separation but requires deploying a second SPA.

For phase 1 (TVP demo), **option A** is faster — one frontend change, swap by URL parameter.

---

## Step 7 — Add the EU operator to the `.well-known` operator directory

Foundation operator registry lives at `https://ledgerproofhq.io/.well-known/lpr-operators.json`. Add an entry:

```json
{
  "operators": [
    {
      "name":              "LedgerProof Foundation US Calendar",
      "region":            "us-east",
      "did":               "did:web:api.ledgerproofhq.io",
      "api_base":          "https://api.ledgerproofhq.io",
      "anchor_substrate":  "bitcoin-mainnet",
      "active":            true
    },
    {
      "name":              "LedgerProof Foundation EU Calendar",
      "region":            "eu",
      "did":               "did:web:api-eu.ledgerproofhq.io",
      "api_base":          "https://api-eu.ledgerproofhq.io",
      "anchor_substrate":  "bitcoin-mainnet",
      "data_residency":    "EU",
      "lpr_version":       "1.0",
      "eu_ai_act_50_supported": true,
      "gdpr_article_17_supported": true,
      "active":            true
    }
  ]
}
```

This makes the EU operator discoverable by verifiers and clients without code changes on their end.

---

## Founder-action checklist

1. [ ] Confirm DNS provider for `ledgerproofhq.io` (Cloudflare? Route53?) by checking the dashboard you used originally
2. [ ] Add `api-eu` CNAME record per Step 2
3. [ ] After Test 1 of smoke-test plan passes via fly.dev hostname, run `fly certs create` (Step 3) — agent can do this
4. [ ] Verify HTTPS resolution per Step 4
5. [ ] (Later) Update publish.ledgerproofhq.io to support region routing per Step 6
6. [ ] (Later) Publish `.well-known/lpr-operators.json` per Step 7

Steps 1, 2, 5, 6 require you. Steps 3, 4 the agent can run.

---

*All other agent-side steps can be executed automatically once the CNAME is in place and DNS has propagated.*
