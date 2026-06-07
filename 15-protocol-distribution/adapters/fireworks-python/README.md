# ledgerproof-fireworks

LedgerProof adapter for the [Fireworks AI](https://fireworks.ai/) Python SDK
(`fireworks-ai>=0.15`).

Cryptographic transparency receipts for EU AI Act **Article 50** evidence,
emitted on a **side channel** so the underlying Fireworks response is never
modified.

This adapter is positioned for **open-model inference deployers**: Fireworks AI
serves many of the leading open-weights models (Meta Llama 3.x, Mixtral, Qwen,
DeepSeek, FireFunction, Black Forest Labs FLUX, and more). Because the model
provider and the inference host are usually different legal entities, this
adapter ships a dedicated `open_model_hosted/v1` schema that records both:

- the **underlying open-model provider** (Meta, Mistral AI, Alibaba/Qwen,
  DeepSeek, Black Forest Labs/FLUX, etc.), and
- the **hosting attribution** (Fireworks AI serving the inference).

Article 50 deployers can use this distinction to keep their transparency
evidence accurate about *who built* the model and *who served* it.

---

## C1 disclaimer (read this first)

> LedgerProof is an **open cryptographic protocol**. It is **NOT endorsed by any
> regulator**. It does **NOT confer the Article 40 presumption of conformity**.
> Using LedgerProof does **NOT** make a deployer compliant with the EU AI Act on
> its own; it only produces tamper-evident receipts of disclosure events that a
> deployer or counterparty can later verify offline.
>
> This adapter is also **NOT endorsed by, affiliated with, or certified by
> Fireworks AI, Inc.** "Fireworks AI" and the names of open-weights models
> hosted on Fireworks (Llama, Mixtral, Qwen, DeepSeek, FireFunction, FLUX, etc.)
> are trademarks of their respective owners. We are a third-party adapter that
> consumes the public `fireworks-ai` Python SDK as a normal user would.

---

## Install

```bash
pip install ledgerproof-fireworks
```

You will also need the standard Fireworks client (declared as a dependency):

```bash
pip install fireworks-ai
export FIREWORKS_API_KEY=fw_...
```

Python 3.10+.

---

## 60-second quickstart

```python
from fireworks_ledgerproof import LedgerProofFireworks, RegulatoryContext

client = LedgerProofFireworks(
    deployer_id="acme-eu",
    api_key="fw_...",
    regulatory_context=RegulatoryContext(
        article_50_paragraph="1",
        deployer_jurisdiction="DE",
        end_user_disclosure_made=True,
    ),
)

response = client.chat.completions.create(
    model="accounts/fireworks/models/llama-v3p1-70b-instruct",
    messages=[{"role": "user", "content": "What is the EU AI Act?"}],
)
print(response.choices[0].message.content)
# A signed receipt was emitted on the side channel (default: stdout logger).
```

## Streaming

```python
stream = client.chat.completions.create(
    model="accounts/fireworks/models/llama-v3p1-70b-instruct",
    messages=[{"role": "user", "content": "Stream me a haiku."}],
    stream=True,
)
for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
# Receipt is finalized when the stream ends (or when you break out).
```

## Image generation (FLUX)

```python
from fireworks_ledgerproof import LedgerProofFireworks

client = LedgerProofFireworks(
    deployer_id="acme-eu",
    api_key="fw_...",
    schema="flux_image_generation/v1",
)

image = client.image.generate(
    model="accounts/fireworks/models/flux-1-schnell-fp8",
    prompt="A photograph of an alpine lake at sunrise.",
)
# A flux_image_generation/v1 receipt is emitted with provider="fireworks"
# and underlying_model_provider="black-forest-labs".
```

## Open-model hosted attribution

```python
from fireworks_ledgerproof import LedgerProofFireworks, OpenModelAttribution

client = LedgerProofFireworks(
    deployer_id="acme-eu",
    api_key="fw_...",
    schema="open_model_hosted/v1",
    open_model=OpenModelAttribution(
        underlying_model_family="llama",
        underlying_model_provider="meta",
        host_provider="fireworks",
        model_license="llama-3.1-community",
        weights_origin="https://huggingface.co/meta-llama/Llama-3.1-70B-Instruct",
    ),
)
```

---

## Design discipline (the four hard rules)

| Constraint | What it means here |
|------------|--------------------|
| **C1** | No regulator endorsement, no Article 40 presumption, no Fireworks AI endorsement. |
| **C4** | Receipts verify **offline**. No phone-home, no LedgerProof-operated endpoint required. |
| **C6** | Stream-aware. Hashing is incremental over text deltas; we never buffer full bodies. |
| **C7** | **Side-channel emission only.** We never mutate the `fireworks` response object. |

If a receipt cannot be built or emitted, the calling code path is **never**
broken. The Fireworks response is returned unchanged.

---

## Receipt schemas

This adapter ships four v1 schemas:

| Schema | Article 50 paragraph | When to use |
|--------|---------------------|-------------|
| `chatbot_session/v1`        | 50(1) | Direct chat interactions with a natural person |
| `generated_content/v1`      | 50(2) | Synthetic content output (text) |
| `open_model_hosted/v1`      | 50(1) (variant) | Records underlying open-model + Fireworks hosting attribution |
| `flux_image_generation/v1`  | 50(2) | FLUX image models hosted on Fireworks |

All schemas share a common signed envelope (Ed25519 over deterministic CBOR,
RFC 8949 §4.2).

---

## GDPR guardrails

Receipts are designed to be **safe to leak**:

- Raw prompt / response text is **NEVER** stored in a receipt. Content is
  referenced via SHA-256 hashes only.
- `deployer_id`, `user_session_id`, `receipt_id` reject email-shaped strings
  (direct-identifier guard — GDPR Art. 4(1) / Art. 5(1)(c) data minimisation).
- Identifier fields are pattern-bounded (`[A-Za-z0-9._:-/+]`, ≤128 chars).
- Free-text fields are length-bounded (≤512 chars).

---

## Signers

The MVP ships an **ephemeral Ed25519 signer** suitable for development and
side-by-side validation. Stubs are included for:

- AWS KMS
- GCP KMS
- Azure Key Vault

Production deployments will swap the signer via the `Signer` protocol.

---

## Verifying a receipt offline (C4)

```python
import base64
from fireworks_ledgerproof import verify
from fireworks_ledgerproof.canonical import canonical_encode

canonical = canonical_encode(signed["receipt"])
sig = base64.b64decode(signed["signature_b64"])
ok = verify(public_key_bytes, canonical, sig)
```

---

## License

Apache 2.0. See `LICENSE`.
