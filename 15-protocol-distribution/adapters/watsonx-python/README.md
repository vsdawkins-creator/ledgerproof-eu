# ledgerproof-watsonx

LedgerProof adapter for the **IBM watsonx.ai** Python SDK. Emits signed,
side-channel cryptographic receipts for AI interactions that fall under
EU AI Act Article 50.

- Wraps `ibm_watsonx_ai.foundation_models.ModelInference` as a drop-in.
- Supports `chat`, `chat_stream`, `generate_text`, and `generate_text_stream`.
- Captures **EU-DE (Frankfurt) data residency**, watsonx **project / tenant /
  deployment-space** attribution, and **IBM Granite open-weights** model
  provenance.
- Ed25519 in-process signing by default; IBM Key Protect and IBM Cloud Hyper
  Protect Crypto Services (HPCS, FIPS 140-2 Level 4) signer interfaces are
  documented stubs for production wiring.
- CBOR canonical encoding (RFC 8949 §4.2). Offline-verifiable (constraint C4).
- GDPR-safe by default: no raw prompt or response text in receipts, only
  SHA-256 references. Heavy validators reject malformed identifiers up front.

## Status

`0.1.0` — Phase 1 MVP. API surface stable for the four entrypoints listed
above. Not yet semver-locked.

## Disclaimers (read these)

- **Not endorsed by IBM.** LedgerProof is an open protocol developed by the
  LedgerProof Foundation (in formation). IBM has not reviewed, certified, or
  endorsed this adapter, this protocol, or any receipt it produces. References
  to "watsonx", "watsonx.ai", "Granite", "IBM Cloud", trademarks, and model
  IDs are for interoperability only.
- **Not an endorsement by any EU regulator.** Production and emission of
  LedgerProof receipts does not constitute compliance with the EU AI Act, nor
  any regulator finding. The protocol is voluntary.
- **No Article 40 presumption of conformity.** This protocol is not a
  harmonised standard within the meaning of Article 40 of the EU AI Act and
  cannot create a presumption of conformity.
- **Deployer remains responsible.** Receipts are evidentiary artifacts. Use
  of this adapter does not transfer or reduce any Article 50 obligation of
  the deployer or of any upstream model provider.
- **Not endorsed by any upstream model provider** accessible via watsonx.ai
  (IBM Granite, Meta Llama, Mistral, Google, Core42, ELYZA, SDAIA, etc.).
  Model IDs are recorded structurally only; LedgerProof does not represent
  any provider's compliance posture.

## Install

```bash
pip install ledgerproof-watsonx
```

Or, from source:

```bash
pip install -e .
```

## Quick start

```python
from ibm_watsonx_ai import Credentials
from ledgerproof_watsonx import LedgerProofModelInference

credentials = Credentials(
    url="https://eu-de.ml.cloud.ibm.com",   # Frankfurt — EU data residency
    api_key="<your-iam-api-key>",
)

model = LedgerProofModelInference(
    deployer_id="acme-eu-bank",
    model_id="ibm/granite-3-8b-instruct",
    credentials=credentials,
    project_id="<watsonx-project-uuid>",
    regulatory_context={
        "article_50_paragraph": "1",
        "deployer_jurisdiction": "DE",
        "end_user_disclosure_made": True,
    },
)

response = model.chat(
    messages=[{"role": "user", "content": "Hallo!"}],
)
# Response is unchanged; receipt has already been emitted on stdout.
```

## EU-DE data residency

watsonx.ai's `eu-de` (Frankfurt) region is the primary EU data-residency
target for German enterprise deployers. The adapter switches the receipt
schema to `eu_data_residency/v1` and records that the call ran in an EU
region, alongside the watsonx project ID and an optional tenant identifier.

```python
model = LedgerProofModelInference(
    deployer_id="acme-eu-bank",
    model_id="ibm/granite-3-8b-instruct",
    credentials=Credentials(url="https://eu-de.ml.cloud.ibm.com", api_key="..."),
    project_id="<watsonx-project-uuid>",
    attest_residency=True,        # → emits eu_data_residency/v1
    sccs_in_place=True,           # Standard Contractual Clauses
    tenant_id="acme-de-tenant-hash",
)
```

`eu-gb` (London) is recognised as adjacent EEA but **not** as EU; the
`is_eu_region(...)` helper returns `False` for `eu-gb` after Brexit. Use the
looser `is_eea_or_adjacent(...)` if your compliance posture groups UK with EU.

## IBM Granite open-weights attestation

IBM Granite 3.x is Apache-2.0 licensed and the weights are published on
Hugging Face. For Article 50 disclosure, this is materially different from a
closed-weights API call: the deployer can independently audit and reproduce
the underlying model. The `granite_open_model/v1` schema records this fact.

```python
model = LedgerProofModelInference(
    deployer_id="acme-eu-bank",
    model_id="ibm/granite-3-8b-instruct",
    credentials=Credentials(url="https://eu-de.ml.cloud.ibm.com", api_key="..."),
    project_id="<watsonx-project-uuid>",
    attest_granite_open_weights=True,   # → emits granite_open_model/v1
)
```

Both flags can be combined; if `attest_residency=True` the residency schema
wins and the open-weights attestation rides as an additional field.

## Streaming

```python
stream = model.chat_stream(
    messages=[{"role": "user", "content": "Tell me a story"}],
)
for chunk in stream:
    print(chunk, end="")
# One receipt emitted after the stream is fully drained (constraint C6).
```

## Decorator pattern

```python
from ledgerproof_watsonx import lpr_track

@lpr_track(
    deployer_id="acme-eu-bank",
    region="eu-de",
    model_id="ibm/granite-3-8b-instruct",
    project_id="<watsonx-project-uuid>",
    user_message_kwarg="prompt",
)
def summarize(prompt: str) -> dict:
    return model.chat(messages=[{"role": "user", "content": prompt}])
```

## Manual emission

```python
from ledgerproof_watsonx import emit_receipt

signed = emit_receipt(
    response=watsonx_response_dict,
    deployer_id="acme-eu-bank",
    model_id="ibm/granite-3-8b-instruct",
    region="eu-de",
    project_id="<watsonx-project-uuid>",
    user_message_text="Some prompt",
)
```

## Architecture constraints

| ID | Constraint                                  | This adapter                                                                                       |
| -- | ------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| C1 | No regulator / provider endorsement         | Disclaimers above. **Not endorsed by IBM.** No claim of presumption of conformity.                 |
| C4 | Local verification only                     | Verifier checks signature + canonical CBOR offline against the bundled Ed25519 public key.         |
| C6 | Stream-aware signing                        | `IncrementalTextHasher` feeds `chat_stream` and `generate_text_stream` deltas; one receipt at end. |
| C7 | Side-channel emission only                  | Receipts go to `LogEmitter` / `WebhookEmitter` / `IbmCloudLogsEmitter` etc. NEVER into the response. |

## GDPR posture (heavy)

IBM enterprise buyers care about GDPR. This adapter defaults to:

- SHA-256 content references only — raw prompt/response text NEVER stored in
  receipts.
- Pydantic validators reject malformed identifiers and oversized free-text
  fields at receipt-construction time.
- The `tenant_id` field in `DataResidencyAttestation` is intended for a
  **hashed** account identifier, not a raw IBM Cloud account number.
- The `eu_data_residency/v1` schema cross-checks attested region against the
  region parsed from `Credentials.url` (catches drift between deployer claim
  and actual endpoint).

## License

Apache-2.0. See [LICENSE](./LICENSE).
