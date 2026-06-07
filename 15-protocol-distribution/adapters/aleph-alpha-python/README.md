# ledgerproof-aleph-alpha

LedgerProof side-channel adapter for the [Aleph Alpha Python SDK](https://github.com/Aleph-Alpha/aleph-alpha-client),
producing EU AI Act Article 50 transparency receipts for completions from Luminous and other
Aleph Alpha models — including on-premises sovereign deployments operated inside Germany
and the broader EU.

> **Why Aleph Alpha + LedgerProof?**
> Aleph Alpha is Germany's flagship sovereign-AI foundation-model company, built for
> European data residency, on-premises operation in regulated environments (financial
> services, public sector, defence, healthcare), and integration with German enterprise
> governance frameworks. LedgerProof's `on_prem_sovereign_deployment/v1` schema captures
> the hosting jurisdiction and operator attestation alongside every receipt — strategic
> for BaFin / Bundesbank / BSI conversations and for organisations that need a verifiable
> chain of provenance proving an AI interaction never left a designated jurisdiction.

---

## C1 — Independence disclaimer

LedgerProof is an independent open cryptographic protocol stewarded by the
**LedgerProof Foundation** (Stichting, the Netherlands). It is **not** endorsed
by, certified by, or affiliated with:

- the European Commission, the EU AI Office, ENISA, or any EU Member State regulator
- BaFin, Bundesbank, BSI, or any German federal authority
- Aleph Alpha GmbH

LedgerProof receipts are **not** a Conformity Assessment, a CE-marking artefact, or a
presumption of conformity under Article 40 of Regulation (EU) 2024/1689. Receipts are
**tamper-evident transparency evidence** intended to support — not replace — a
provider's or deployer's Article 50 obligations.

This adapter does **not** modify any model response (constraint **C7**: side-channel
emission only). It observes the prompt and completion, then emits a separately signed
receipt over a side-channel emitter you configure.

---

## Install

```bash
pip install ledgerproof-aleph-alpha
```

Python 3.10+ required.

---

## Quick start (sync)

```python
from aleph_alpha_client import Client, CompletionRequest, Prompt
from aleph_alpha_ledgerproof import LedgerProofAlephAlpha

upstream = Client(token="YOUR_TOKEN", host="https://api.aleph-alpha.com")

client = LedgerProofAlephAlpha(
    upstream,
    article="50(2)",
    deployer_id="acme-de-frankfurt",
)

req = CompletionRequest(
    prompt=Prompt.from_text("Briefly explain Article 50 transparency obligations."),
    maximum_tokens=64,
)
resp = client.complete(req, model="luminous-base")

print(resp.completions[0].completion)
# receipt is emitted to the configured emitter (default: stdout JSON)
```

The response object returned by `complete()` is **the exact upstream
`CompletionResponse`**. No fields are added, removed, or reordered (C7).

## Async

```python
from aleph_alpha_client import AsyncClient, CompletionRequest, Prompt
from aleph_alpha_ledgerproof import LedgerProofAsyncAlephAlpha

async with AsyncClient(token="YOUR_TOKEN", host="https://api.aleph-alpha.com") as up:
    client = LedgerProofAsyncAlephAlpha(up, article="50(2)")
    resp = await client.complete(req, model="luminous-base")
```

## Decorator pattern

```python
from aleph_alpha_ledgerproof import lpr_track

@lpr_track(article="50(1)", schema="chatbot_session/v1")
def chat(prompt: str) -> str:
    req = CompletionRequest(prompt=Prompt.from_text(prompt), maximum_tokens=128)
    r = upstream.complete(req, model="luminous-base")
    return r.completions[0].completion
```

## Manual emission

```python
from aleph_alpha_ledgerproof import emit_receipt

emit_receipt(
    article="50(1)",
    schema="on_prem_sovereign_deployment/v1",
    prompt_text=prompt,
    completion_text=output,
    model="luminous-supreme",
    extra={
        "hosting_jurisdiction": "DE",
        "operator": "Acme Bank AG",
        "sovereignty_attestation": "on-prem-frankfurt-dc01",
    },
)
```

---

## Schemas

| Schema                                  | Article 50 scope                                                | When to use                                              |
|-----------------------------------------|-----------------------------------------------------------------|----------------------------------------------------------|
| `chatbot_session/v1`                    | 50(1) — natural-person interaction disclosure                   | Any chatbot/agent surface                                |
| `generated_content/v1`                  | 50(2) — synthetic content marking                               | Generated text, summaries, drafts                        |
| `on_prem_sovereign_deployment/v1`       | 50(1) variant — sovereign / on-prem operator attestation        | German on-prem Luminous, BaFin-supervised deployments    |

All three apply Pydantic GDPR validators (no raw PII content in receipt payloads —
only hashes; jurisdiction codes constrained to ISO 3166-1 alpha-2).

---

## How it works

1. You call `client.complete(...)` exactly as you would with the upstream Aleph Alpha SDK.
2. The adapter forwards the call **unmodified** and captures the prompt + completion (C7).
3. It computes an incremental SHA-256 over the canonical CBOR encoding (C6: stream-safe).
4. It signs the digest with an **ephemeral Ed25519 key** (C4: local verification only).
5. It hands the receipt to an `Emitter` (default: stdout JSON). You can plug in
   Kafka, S3, an HSM-backed signer, or a Foundation-operated witness later.

The response payload returned to you is byte-identical to upstream.

---

## Local verification (C4)

```python
from aleph_alpha_ledgerproof import verify_receipt

ok = verify_receipt(receipt_json)
assert ok is True
```

There is **no remote attestation service**, no phone-home, no telemetry. Verification
is purely local and offline.

---

## License

Apache 2.0 — see `LICENSE`.
