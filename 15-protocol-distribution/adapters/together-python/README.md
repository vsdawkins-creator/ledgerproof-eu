# ledgerproof-together

LedgerProof adapter for the [Together.ai](https://www.together.ai/) Python SDK
(`together>=1.3`).

Cryptographic transparency receipts for EU AI Act **Article 50** evidence,
emitted on a **side channel** so the underlying Together.ai response is never
modified.

This adapter is positioned for **open-model inference deployers**: Together hosts
many of the leading open-weights models (Meta Llama 3 / 3.3, Mistral, Qwen,
DeepSeek, FLUX, and more). Because the model provider and the inference host
are often different legal entities, this adapter ships a dedicated
`open_model_inference/v1` schema that records both:

- the **underlying open-model provider** (Meta, Mistral AI, Alibaba/Qwen,
  DeepSeek, Black Forest Labs/FLUX, etc.), and
- the **hosting attribution** (Together.ai serving the inference).

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
> Together AI Inc.** "Together.ai" and the names of open-weights models hosted
> on Together (Llama, Mistral, Qwen, DeepSeek, FLUX, etc.) are trademarks of
> their respective owners. We are a third-party adapter that consumes the
> public `together` Python SDK as a normal user would.

---

## Install

```bash
pip install ledgerproof-together
```

You will also need the standard Together client (declared as a dependency):

```bash
pip install together
export TOGETHER_API_KEY=sk-...
```

Python 3.10+.

---

## 60-second quickstart

```python
from together_ledgerproof import LedgerProofTogether, RegulatoryContext

client = LedgerProofTogether(
    deployer_id="acme-eu",
    regulatory_context=RegulatoryContext(
        article_50_paragraph="1",
        deployer_jurisdiction="DE",
        end_user_disclosure_made=True,
    ),
)

response = client.chat.completions.create(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
    messages=[{"role": "user", "content": "What is the EU AI Act?"}],
)
print(response.choices[0].message.content)
# A signed receipt was emitted on the side channel (default: stdout logger).
```

## Streaming

```python
stream = client.chat.completions.create(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
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
from together_ledgerproof import LedgerProofTogether

client = LedgerProofTogether(
    deployer_id="acme-eu",
    schema="image_generation/v1",
)

image = client.images.generate(
    model="black-forest-labs/FLUX.1-schnell-Free",
    prompt="A photograph of an alpine lake at sunrise.",
    width=1024,
    height=1024,
)
# A generated_content/v1-style receipt is emitted with provider="together"
# and underlying_model_provider="black-forest-labs".
```

## Open-model attribution

```python
from together_ledgerproof import LedgerProofTogether, OpenModelAttribution

client = LedgerProofTogether(
    deployer_id="acme-eu",
    schema="open_model_inference/v1",
    open_model=OpenModelAttribution(
        underlying_model_family="llama",
        underlying_model_provider="meta",
        host_provider="together",
        model_license="llama-3.3-community",
        weights_origin="https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct",
    ),
)
```

---

## Design discipline (the four hard rules)

| Constraint | What it means here |
|------------|--------------------|
| **C1** | No regulator endorsement, no Article 40 presumption, no Together.ai endorsement. |
| **C4** | Receipts verify **offline**. No phone-home, no LedgerProof-operated endpoint required. |
| **C6** | Stream-aware. Hashing is incremental over text deltas; we never buffer full bodies. |
| **C7** | **Side-channel emission only.** We never mutate the `together` response object. |

If a receipt cannot be built or emitted, the calling code path is **never**
broken. The Together response is returned unchanged.

---

## Receipt schemas

This adapter ships four v1 schemas:

| Schema | Article 50 paragraph | When to use |
|--------|---------------------|-------------|
| `chatbot_session/v1`     | 50(1) | Direct chat interactions with a natural person |
| `generated_content/v1`   | 50(2) | Synthetic content output (text, image, audio) |
| `open_model_inference/v1`| 50(1) (variant) | Records underlying open-model + Together hosting attribution |
| `image_generation/v1`    | 50(2) | FLUX and other image models hosted on Together |

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
from together_ledgerproof import verify
from together_ledgerproof.canonical import canonical_encode

canonical = canonical_encode(signed["receipt"])
sig = base64.b64decode(signed["signature_b64"])
ok = verify(public_key_bytes, canonical, sig)
```

---

## License

Apache 2.0. See `LICENSE`.
