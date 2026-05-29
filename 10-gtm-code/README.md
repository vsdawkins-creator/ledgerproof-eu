# LedgerProof GTM — Executable Code

Operationalizes the [GTM master plan](../08-gtm/00-MASTER-PLAN.md) and the [integrator](../PLAN.md). Every outbound, every persona variant, every tracked response is produced by this package.

## Why this exists

The plan has 19 commercial artifacts and a documented cadence (Tue/Wed sends, no-Mon-no-Fri rule, 7-business-day silence triggers a different-persona retouch, 14-day silence switches to artifact-send, two-touch cap per individual). Running that by hand drifts. This package runs it.

## What it does

- Renders persona-aware outbound emails from the artifact templates
- Schedules sends inside the Tue/Wed 09:00–10:30 CET window
- Anchors every outbound artifact as a LedgerProof Receipt (dogfood — Foundation publishes its own communications as receipts)
- Tracks per-account state across personas (GC, CRO/CCO, MLOps)
- Enforces the two-touch cap per individual
- Produces the Shadow AI Inventory PDF and the Audit-Ready Compliance Stamp summary on demand
- Powers reference-customer playbook tier transitions
- CLI surface: `lpr-gtm <command>`

## Install

```bash
cd 10-gtm-code
pip install -e .
```

## Quickstart

```bash
# Initialize tracking database
lpr-gtm init

# Import accounts from the 50 named-target list
lpr-gtm accounts import examples/seed_accounts.csv

# Render an outbound for a single account
lpr-gtm render --account "[Account]" --persona gc --send-date 2026-07-28

# Schedule the Day-30 outbound wave
lpr-gtm wave plan --milestone day-30 --output ./outbox

# Send what's planned for today (dry-run by default)
lpr-gtm wave send --execute
```

## Layout

```
10-gtm-code/
├── README.md
├── pyproject.toml
├── gtm/
│   ├── __init__.py
│   ├── cli.py            ← Click-based CLI
│   ├── personas.py       ← Persona definitions + skill alignment
│   ├── sequences.py      ← Timing/cadence rules
│   ├── rendering.py      ← Jinja-based template rendering
│   ├── tracking.py       ← SQLite state for accounts + touches
│   ├── anchoring.py      ← LedgerProof Receipt anchoring (real SDK + mock backend)
│   ├── artifacts.py      ← PDF + HTML + JSON artifact builders
│   ├── brand.py          ← Brand voice constraints (Navy/Mint/Cream/Iowan)
│   └── templates/
│       ├── emails/       ← Persona-targeted email templates
│       ├── one_pagers/   ← Shadow AI Inventory, persona one-pagers
│       ├── whitepapers/  ← FSI sector deep-dive
│       └── stamps/       ← Audit-Ready Compliance Stamp variants
├── tests/                ← pytest; covers timing, rendering, anchoring, tracking
├── examples/
│   └── seed_accounts.csv
└── scripts/
    └── seed_accounts.py  ← bootstrap the 50 named targets
```

## Invariants (carried from PLAN.md)

- Anchoring uses the real `ledgerproof` SDK when `LPR_API_KEY` is in env; falls back to a deterministic mock when absent (dev-mode only — refuses to run in `LPR_ENV=prod`)
- No outbound email body contains email addresses in `deployer_id`, `reviewer_role`, or `review_rationale` — schema-validated at render time
- Send window enforcement is non-overridable except by `--force-send` (logs a warning + records the override in the tracking DB)
- Two-touch cap per individual is enforced at `wave send`; exceeding requires `--ack-cap` flag

## Status

Day-30 outbound flows are wired end-to-end. Day-60 pilot SOW generation and Day-90 marketplace listing renderers are scaffolded but not yet wired to live submission APIs. Day-180 Series A pack assembly is on the roadmap as a follow-on.
