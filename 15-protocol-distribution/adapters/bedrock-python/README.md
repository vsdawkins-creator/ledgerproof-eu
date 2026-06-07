# ledgerproof-bedrock

LedgerProof adapter for the **AWS Bedrock Runtime** Python SDK (boto3). Emits
signed, side-channel cryptographic receipts for AI interactions that fall under
EU AI Act Article 50.

- Wraps `boto3.client("bedrock-runtime")` as a drop-in.
- Supports legacy (`invoke_model`, `invoke_model_with_response_stream`) and the
  newer unified Converse API (`converse`, `converse_stream`).
- Captures **provider attribution** (Anthropic / Meta / Mistral / Amazon /
  Cohere / AI21 / Stability) plus **region**.
- Optional **EU data residency attestation** schema for eu-west-1, eu-central-1,
  eu-north-1, and other EU regions.
- Ed25519 in-process signing by default; AWS KMS / GCP KMS signer interfaces
  documented for production wiring.
- CBOR canonical encoding (RFC 8949 §4.2). Offline-verifiable (constraint C4).
- GDPR-safe by default: no raw prompt or response text in receipts, only
  SHA-256 references.

## Status

`0.1.0` — Phase 1 MVP. API surface stable for the four entrypoints listed
above. Not yet semver-locked.

## Disclaimers (read these)

- **Not an endorsement by AWS.** LedgerProof is an open protocol developed by
  the LedgerProof Foundation (in formation). Amazon Web Services has not
  reviewed, certified, or endorsed this adapter, this protocol, or any receipt
  it produces. References to "Bedrock", "AWS", trademarks, and model IDs are
  for interoperability only.
- **Not an endorsement by any EU regulator.** Production and emission of
  LedgerProof receipts does not constitute compliance with the EU AI Act, nor
  any regulator finding. The protocol is voluntary.
- **No Article 40 presumption of conformity.** This protocol is not a
  harmonised standard within the meaning of Article 40 of the EU AI Act and
  cannot create a presumption of conformity.
- **Deployer remains responsible.** Receipts are evidentiary artifacts. Use of
  this adapter does not transfer or reduce any Article 50 obligation of the
  deployer or of any upstream model provider.
- **Not endorsed by any upstream model provider** accessible via Bedrock
  (Anthropic, Meta, Mistral, Amazon Titan, Cohere, AI21, Stability AI). Model
  IDs are recorded structurally only; LedgerProof does not represent any
  provider's compliance posture.

## Install

```bash
pip install ledgerproof-bedrock
```

Or, from source:

```bash
pip install -e .
```

## Quick start

```python
import boto3, json
from bedrock_ledgerproof import LedgerProofBedrockClient

raw = boto3.client("bedrock-runtime", region_name="eu-west-1")
client = LedgerProofBedrockClient(
    deployer_id="acme-eu-bank",
    client=raw,
    regulatory_context={
        "article_50_paragraph": "1",
        "deployer_jurisdiction": "DE",
        "end_user_disclosure_made": True,
    },
)

response = client.invoke_model(
    modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [{"role": "user", "content": "Hallo!"}],
        "max_tokens": 100,
    }),
)
# Response body is unchanged; receipt has already been emitted on stdout.
```

## Converse API

```python
from bedrock_ledgerproof import make_client

client = make_client(deployer_id="acme-eu-bank", region_name="eu-west-1")

response = client.converse(
    modelId="mistral.mistral-large-2402-v1:0",
    messages=[{"role": "user", "content": [{"text": "Bonjour"}]}],
)
```

`make_client(...)` returns a client with both legacy and Converse methods
wired up.

## EU region residency

```python
from bedrock_ledgerproof import LedgerProofBedrockClient

client = LedgerProofBedrockClient(
    deployer_id="acme-eu-bank",
    region_name="eu-west-1",
    attest_residency=True,        # emits eu_aws_data_residency/v1
    sccs_in_place=True,
)
```

This swaps the receipt schema to `eu_aws_data_residency/v1` and records that
the call ran in an EU region. The verifier compares the deployer's attested
region with the region pulled from the boto3 client config to catch drift.

## Decorator pattern

```python
from bedrock_ledgerproof import lpr_track

@lpr_track(
    deployer_id="acme-eu-bank",
    region="eu-west-1",
    model_id="meta.llama3-70b-instruct-v1:0",
    user_message_kwarg="prompt",
)
def llama_summarize(prompt: str) -> dict:
    raw = boto3.client("bedrock-runtime", region_name="eu-west-1")
    resp = raw.invoke_model(
        modelId="meta.llama3-70b-instruct-v1:0",
        body=json.dumps({"prompt": prompt, "max_gen_len": 200}),
    )
    return json.loads(resp["body"].read())
```

## Manual emission

```python
from bedrock_ledgerproof import emit_receipt

signed = emit_receipt(
    response=decoded_body,
    deployer_id="acme-eu-bank",
    model_id="amazon.titan-text-express-v1",
    region="eu-central-1",
    user_message_text="Some prompt",
)
```

## Cross-provider note

Bedrock is the only AWS-native gateway to multiple AI providers. The
`bedrock_cross_provider/v1` schema records the **upstream provider** alongside
the Bedrock-side model ID, so a deployer using Bedrock to invoke Anthropic,
Meta, and Mistral models from a single application produces receipts that are
distinguishable, queryable, and auditable per provider.

## Architecture constraints

| ID | Constraint                                  | This adapter                                                                                       |
| -- | ------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| C1 | No regulator / provider endorsement         | Disclaimers above. No claim of presumption of conformity.                                          |
| C4 | Local verification only                     | Verifier checks signature + canonical CBOR offline against the bundled Ed25519 public key.         |
| C6 | Stream-aware signing                        | `IncrementalTextHasher` feeds Converse stream deltas and legacy EventStream `chunk` bytes.         |
| C7 | Side-channel emission only                  | Receipts go to `LogEmitter` / `WebhookEmitter` / `CloudWatchEmitter` etc. NEVER into the response. |

## License

Apache-2.0. See [LICENSE](./LICENSE).
