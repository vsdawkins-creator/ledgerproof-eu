# LedgerProof — Independent Calendar Operator Setup Guide

**Version:** 1.0
**Audience:** Organizations wishing to operate an independent LPR v1.0 calendar operator
**Prerequisites:** Bitcoin full node OR Electrum/Bitcoin RPC access; PostgreSQL 14+; Python 3.11+

---

## What is a calendar operator?

A LedgerProof calendar operator is a server that:

1. **Receives** LPR receipt hashes submitted by issuers
2. **Aggregates** those hashes into a Merkle tree (RFC 6962 construction)
3. **Anchors** the Merkle root to Bitcoin mainnet via an OP_RETURN transaction once per anchor window
4. **Serves** Merkle inclusion proofs to verifiers and receipt holders

Running an independent calendar operator:
- Strengthens the LPR ecosystem's claim that verification requires no single party
- Allows your organization to anchor receipts on your own Bitcoin address
- Provides a backup anchor for receipts if the Foundation-operated calendar is unavailable
- Can be required by enterprise customers under their own DORA/GDPR data residency policies

The LedgerProof Foundation's calendar at `calendar.ledgerproofhq.io` is the default operator. Independent operators are additional, not replacements — receipts may be anchored on multiple calendars simultaneously.

---

## Architecture overview

```
┌─────────────────────────────────────────────────────────────┐
│                  INDEPENDENT CALENDAR OPERATOR               │
│                                                             │
│  ┌──────────────┐    ┌───────────────┐    ┌─────────────┐  │
│  │  Receipt     │    │  Merkle Tree  │    │  Anchor     │  │
│  │  Receiver    │───▶│  Builder      │───▶│  Worker     │  │
│  │  (HTTP API)  │    │  (RFC 6962)   │    │  (Bitcoin)  │  │
│  └──────────────┘    └───────────────┘    └─────────────┘  │
│         │                    │                   │          │
│         ▼                    ▼                   ▼          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │             PostgreSQL Receipt Store                  │  │
│  └──────────────────────────────────────────────────────┘  │
│         │                                                   │
│         ▼                                                   │
│  ┌──────────────┐                                          │
│  │  Proof       │  ← Serves inclusion proofs to verifiers  │
│  │  Server      │                                          │
│  └──────────────┘                                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Bitcoin Mainnet │
                    │  OP_RETURN       │
                    └─────────────────┘
```

---

## Prerequisites

### 1. Bitcoin access

Option A (recommended for high-security operators): Run a Bitcoin Core full node.
```bash
bitcoind -daemon -rpcuser=lproperator -rpcpassword=<strong_password> -rpcport=8332
```

Option B (acceptable for lower-throughput operators): Use Electrum or a trusted Bitcoin RPC provider (Blockstream, Mempool.space API, QuickNode, Alchemy).

### 2. Hot wallet for OP_RETURN transactions

You need a Bitcoin address with a small balance to pay transaction fees for the daily anchor. At 2026 fee rates, one OP_RETURN transaction costs approximately 200-2000 satoshis ($0.10-$1.00). Fund the wallet with 0.001 BTC to operate for several years.

**Security:** The hot wallet private key (WIF format) MUST be stored as a secret (environment variable or hardware security module). It MUST NOT appear in configuration files, code, or logs.

### 3. Hardware / cloud

Minimum for a small operator (< 100K receipts/day):
- 2 vCPUs, 4 GB RAM, 100 GB SSD
- Linux (Ubuntu 22.04 LTS recommended)
- Public IP and domain name (e.g., `calendar.yourdomain.com`)
- TLS certificate (Let's Encrypt)

---

## Installation

### Step 1: Clone the operator software

```bash
git clone https://github.com/ledgerproof/lpr-calendar-operator.git
cd lpr-calendar-operator
pip install -r requirements.txt
```

### Step 2: Database setup

```bash
# Install PostgreSQL 14+
sudo apt install postgresql-14

# Create database and user
sudo -u postgres psql << 'EOF'
CREATE DATABASE lpr_calendar;
CREATE USER lpr_operator WITH PASSWORD 'your_strong_password';
GRANT ALL PRIVILEGES ON DATABASE lpr_calendar TO lpr_operator;
EOF

# Run migrations
DATABASE_URL="postgresql://lpr_operator:your_strong_password@localhost/lpr_calendar" \
python -m alembic upgrade head
```

### Step 3: Configure environment

Create `/etc/ledgerproof-operator/env` (not world-readable):

```bash
# Required
DATABASE_URL=postgresql://lpr_operator:password@localhost/lpr_calendar
BITCOIN_NETWORK=mainnet
# BITCOIN_HOT_WALLET_WIF — set only via: sudo systemctl edit ledgerproof-operator
# (or use: export BITCOIN_HOT_WALLET_WIF=<wif> before starting)
BITCOIN_RPC_HOST=127.0.0.1
BITCOIN_RPC_PORT=8332
BITCOIN_RPC_USER=lproperator
BITCOIN_RPC_PASS=your_rpc_password

# Operator identity
OPERATOR_NAME="Your Organization Calendar"
OPERATOR_DID=did:web:calendar.yourdomain.com
OPERATOR_COUNTRY=DE  # ISO 3166-1 alpha-2
OPERATOR_CONTACT=lpr-operator@yourdomain.com

# Anchor settings
ANCHOR_WINDOW_HOURS=24   # How often to anchor (24h default, 1h for High-Assurance profile)
LPR_ANCHOR_PREFIX=LPR1   # Must be exactly "LPR1" — do not change

# API settings
HTTP_PORT=8080
HTTP_HOST=0.0.0.0
TLS_CERT=/etc/letsencrypt/live/calendar.yourdomain.com/fullchain.pem
TLS_KEY=/etc/letsencrypt/live/calendar.yourdomain.com/privkey.pem
ALLOWED_ISSUERS=*  # or restrict to specific API keys
```

Set the hot wallet key separately and securely:
```bash
sudo systemctl edit ledgerproof-operator
# Add:
# [Service]
# Environment="BITCOIN_HOT_WALLET_WIF=<your WIF key here>"
```

### Step 4: Generate operator signing key

The calendar operator MUST sign all Merkle roots it publishes. This key identifies your calendar in the LPR ecosystem.

```bash
python -m lpr_operator.keygen --output /etc/ledgerproof-operator/operator_key.pem
# This generates an Ed25519 keypair. The public key becomes your operator DID.
# Back up the private key securely — if lost, past anchors cannot be attributed to you.
```

### Step 5: Start the service

```bash
# Install systemd service
sudo cp contrib/systemd/ledgerproof-operator.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ledgerproof-operator
sudo systemctl start ledgerproof-operator

# Verify
sudo systemctl status ledgerproof-operator
curl https://calendar.yourdomain.com/health
```

---

## API endpoints exposed by the operator

| Endpoint | Method | Description |
|---|---|---|
| `GET /health` | GET | Health check — returns operator status and last anchor time |
| `POST /submit` | POST | Submit a receipt hash for inclusion in the next Merkle tree |
| `GET /proof/<receipt_id>` | GET | Return the Merkle inclusion proof for a receipt |
| `GET /anchor/<btc_txid>` | GET | Return the Merkle root and all receipt IDs for a given anchor transaction |
| `GET /.well-known/lpr-operator` | GET | Operator identity document (DID document format) |

### Operator identity document (`/.well-known/lpr-operator`)

Your calendar MUST publish an operator identity document at this well-known URL. The document format:

```json
{
  "operator_name": "Your Organization Calendar",
  "operator_did": "did:web:calendar.yourdomain.com",
  "operator_country": "DE",
  "operator_contact": "lpr-operator@yourdomain.com",
  "lpr_version_supported": ["1.0"],
  "anchor_substrate": "bitcoin-mainnet",
  "anchor_window_hours": 24,
  "public_key": "<base64url-encoded Ed25519 public key>",
  "registered_with_foundation": true,
  "registration_date": "2026-07-01"
}
```

---

## Registering with the LedgerProof Foundation

Independent calendar operators SHOULD register with the Foundation to be listed in the official operator registry. Registration:

1. Ensures your operator appears in the Foundation-operated verifier as a trusted anchor source
2. Allows receipt holders to route submissions to your calendar
3. Provides the Foundation with contact information for protocol update notifications

To register:
- Email `operators@ledgerproofhq.io` with:
  - Your `/.well-known/lpr-operator` document URL
  - Your Bitcoin address (for anchor attribution)
  - Your organization name and country
  - The Ed25519 public key of your operator signing key
- The Foundation will verify your setup and add your operator to the registry within 5 business days

---

## Monitoring and operations

### Health monitoring

The operator exposes a `/metrics` endpoint (Prometheus format) at port 9090. Recommended alerts:

| Metric | Alert threshold | Meaning |
|---|---|---|
| `lpr_anchor_age_hours` | > 26 hours | Last anchor is overdue |
| `lpr_pending_receipts` | > 100,000 | Receipt queue is backing up |
| `lpr_btc_balance_sats` | < 10,000 | Hot wallet needs funding |
| `lpr_db_lag_seconds` | > 5 | Database replication lag |

### Bitcoin balance monitoring

```bash
# Check hot wallet balance
python -m lpr_operator.wallet --check-balance
# Output: "Hot wallet balance: 0.00084231 BTC (84,231 satoshis) — sufficient for ~84 daily anchors"
```

### Anchor log

Every anchor transaction is logged to the database and to `/var/log/ledgerproof-operator/anchors.log`:

```
2026-07-01T00:00:15Z INFO Merkle tree built: 48,291 receipts, root=a1b2c3d4...
2026-07-01T00:00:18Z INFO OP_RETURN tx broadcast: txid=5db5c68e...
2026-07-01T00:02:44Z INFO Anchor confirmed: block_height=900122, 1 confirmation
```

---

## Security requirements for EU operators

Operators wishing to serve EU enterprises under DORA and GDPR MUST additionally:

1. **Host in the EU** — the server must be physically located in an EU/EEA member state
2. **TLS 1.3 only** — disable TLS 1.2 and earlier
3. **Data retention policy** — document and enforce retention of receipt records per applicable law (recommended: 10 years for regulatory compliance use cases)
4. **Incident notification** — notify the Foundation at `security@ledgerproofhq.io` within 24 hours of any security incident affecting receipt integrity
5. **Annual key rotation** — rotate the operator Ed25519 signing key annually; publish key rotation events to the Foundation registry

---

## Troubleshooting

**Problem:** `lpr_anchor_age_hours` alert firing — anchor is overdue

Check:
```bash
# Check Bitcoin RPC connectivity
python -m lpr_operator.bitcoin --test-connection

# Check hot wallet balance
python -m lpr_operator.wallet --check-balance

# Check anchor worker logs
journalctl -u ledgerproof-operator -n 100 | grep "anchor"
```

**Problem:** High pending receipt count

The anchor worker batches all pending receipts into one Merkle tree. A high count is normal and expected. The anchor will process all pending receipts in the next anchor window. If the count exceeds 1,000,000, consider reducing `ANCHOR_WINDOW_HOURS` to 1 hour.

**Problem:** Database connection errors

```bash
# Test database connection
DATABASE_URL="..." python -m lpr_operator.db --test
```

---

## Contact and support

- Technical issues: `operators@ledgerproofhq.io`
- Security vulnerabilities: `security@ledgerproofhq.io` (PGP key at ledgerproofhq.io/pgp)
- Protocol questions: `protocol@ledgerproofhq.io`
- Foundation registry: `ledgerproofhq.io/operators`

---

*LedgerProof Foundation · Calendar Operator Setup Guide v1.0 · May 2026*
*Software license: MIT · Documentation license: CC BY 4.0*
