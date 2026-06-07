# ledgerproof-perplexity

LedgerProof adapter for **Perplexity AI**, which exposes an OpenAI-compatible
REST API at `https://api.perplexity.ai`. This package wraps the official
[`openai` Python SDK](https://github.com/openai/openai-python) configured for
that endpoint and emits signed EU AI Act **Article 50** transparency receipts
as a side channel — your Perplexity response is returned unmodified.

```
pip install ledgerproof-perplexity
```

## Why Perplexity matters for Article 50(4)

Perplexity is the most widely adopted **AI search** product on the market. Its
Sonar family (`sonar`, `sonar-pro`, `sonar-reasoning`, `sonar-deep-research`)
performs live web search and returns a `citations` field on every response —
the URLs that grounded the answer.

That citation surface is the single most important hook for Article 50(4) of
the EU AI Act: *"text generated or manipulated by an AI system and published
with the purpose of informing the public on matters of public interest."* The
obligation reduces where the output undergoes human review and a person/entity
holds editorial responsibility, but in every other case the deployer needs to
label the text and (in practice) be ready to explain *which* sources it drew
on. A signed receipt that binds **(prompt, response, citation list)** is the
cleanest way to discharge that evidence burden.

This adapter ships four schemas tuned to Perplexity-specific scenarios:

| Schema                              | Article basis | Use when |
|-------------------------------------|---------------|----------|
| `chatbot_session/v1`                | Art. 50(1)    | Standard conversational Sonar use |
| `generated_content/v1`              | Art. 50(2)    | Synthetic content output |
| `ai_search_with_citations/v1`       | Art. 50(1)+(4) | Sonar live-search; binds citation hash |
| `public_interest_text/v1`           | Art. 50(4)    | AI-generated text published to inform the public, with citation provenance + disclosure + editorial-review attestations |

## 5-minute quickstart

```python
from perplexity_ledgerproof import LedgerProofPerplexity

# Defaults: base_url=https://api.perplexity.ai, api_key=$PPLX_API_KEY
# (PERPLEXITY_API_KEY is also accepted as a fallback env var.)
client = LedgerProofPerplexity(
    deployer_id="urn:eu:deployer:acme-media-de",
    regulatory_context={"schema": "chatbot_session/v1", "jurisdiction": "EU"},
)

resp = client.chat.completions.create(
    model="sonar",
    messages=[{"role": "user", "content": "What is the EU AI Act timeline?"}],
)

print(resp.choices[0].message.content)
# A signed receipt has been emitted to the configured emitter
# (stdout LogEmitter by default).
```

## Three integration patterns

### 1. Client wrapper (recommended)

```python
from perplexity_ledgerproof import (
    LedgerProofPerplexity,
    LedgerProofAsyncPerplexity,
)

client = LedgerProofPerplexity(deployer_id="urn:eu:deployer:acme")
async_client = LedgerProofAsyncPerplexity(deployer_id="urn:eu:deployer:acme")
```

Works with both **non-streaming** (`stream=False`) and **streaming**
(`stream=True`) chat completions. Streaming uses incremental SHA-256
over each chunk (constraint **C6**), and accumulates any citations that
Perplexity attaches to chunks (typically on the final chunk).

### 2. Decorator

```python
import os
from openai import OpenAI
from perplexity_ledgerproof import lpr_track

client = OpenAI(
    api_key=os.environ["PPLX_API_KEY"],
    base_url="https://api.perplexity.ai",
)

@lpr_track(deployer_id="urn:eu:deployer:acme")
def search(question: str, *, messages):
    return client.chat.completions.create(model="sonar", messages=messages)
```

### 3. Manual emission

```python
import os
from openai import OpenAI
from perplexity_ledgerproof import emit_receipt

client = OpenAI(
    api_key=os.environ["PPLX_API_KEY"],
    base_url="https://api.perplexity.ai",
)
resp = client.chat.completions.create(
    model="sonar",
    messages=[{"role": "user", "content": "hi"}],
)
emit_receipt(resp, deployer_id="urn:eu:deployer:acme")
```

## AI search with citation provenance

Perplexity attaches a `citations` field — a list of source URLs — to every
Sonar response. For the citation-aware schemas
(`ai_search_with_citations/v1`, `public_interest_text/v1`) the adapter
**automatically extracts** that list, computes a deterministic SHA-256 over
the lexicographically-sorted URLs, and writes both `citations_sha256` and
`citations_count` into the receipt.

```python
from perplexity_ledgerproof import LedgerProofPerplexity

client = LedgerProofPerplexity(
    deployer_id="urn:eu:deployer:acme-media-de",
    regulatory_context={
        "schema": "ai_search_with_citations/v1",
        "jurisdiction": "EU",
    },
)

resp = client.chat.completions.create(
    model="sonar-pro",
    messages=[{"role": "user", "content": "Brief me on Article 50."}],
)

# resp.citations -> ["https://...", ...]
# Receipt now carries citations_sha256 + citations_count, deterministically
# bound to that URL list.
```

If your auditor requires a custom canonical form for the citation list
(e.g. URL + capture-timestamp tuples), pre-compute the hash and pass it
through `regulatory_context["citations_sha256"]` — the adapter will respect
the deployer-supplied value instead of recomputing it. The deployer is then
responsible for preserving whatever canonical input produced that hash.

## Article 50(4) public-interest text labelling

```python
from perplexity_ledgerproof import LedgerProofPerplexity

client = LedgerProofPerplexity(
    deployer_id="urn:eu:deployer:acme-media-de",
    regulatory_context={
        "schema": "public_interest_text/v1",
        "jurisdiction": "EU",
        "disclosure_label_shown": True,   # we surface an AI-generated label
        "editorial_review": True,         # human editor signed off
        "subject_category": "news.civic",
    },
)
resp = client.chat.completions.create(
    model="sonar-pro",
    messages=[{"role": "user", "content": "Summarise today's EU AI Office update."}],
)
```

The resulting receipt is a single signed artefact that records, at minimum,
the prompt hash, response hash, citation-list hash, disclosure-label
attestation, editorial-review attestation, and subject-category tag — exactly
the surface that a regulator inquiry into Article 50(4) labelling is likely
to probe.

## Custom emitters

```python
from perplexity_ledgerproof import (
    LedgerProofPerplexity,
    WebhookEmitter,
    QueueEmitter,
)

client = LedgerProofPerplexity(
    deployer_id="urn:eu:deployer:acme",
    emitter=WebhookEmitter(url="https://receipts.acme.example/ingest"),
)
```

## Scope and discipline (C1–C8)

This adapter implements the LedgerProof protocol with the following
discipline:

- **C1 — No regulator endorsement.** This package is **not endorsed by** the
  European Commission, the EU AI Office, or any national supervisory
  authority. It does **not** provide an Article 40 presumption of conformity.
- **Not endorsed by Perplexity.** This is an independent adapter built on top
  of Perplexity's publicly documented OpenAI-compatible API. It is **not
  affiliated with, sponsored by, or endorsed by Perplexity AI, Inc.**
  "Perplexity", "Sonar", and related marks are trademarks of their respective
  owner; used here for descriptive interoperability purposes only.
- **C4 — Offline verification.** Receipts are verifiable offline against the
  published protocol public key and Bitcoin OP_RETURN anchor. The adapter
  does not phone home. Citation-list hashes are computed locally from the
  URLs Perplexity returns — the adapter does **not** fetch, validate, or
  archive the cited pages.
- **C6 — Stream-aware signing.** Streaming completions are hashed
  incrementally so the receipt covers the full reconstructed text, and
  citations are accumulated from whichever chunk carries them.
- **C7 — Side-channel only.** This adapter never modifies the Perplexity
  response. Receipts emit through a separate emitter (log/webhook/queue),
  and emitter failures never propagate into the caller path.

### What this adapter does NOT do

- Does **not** address Article 9 (risk management), Article 10 (data
  governance), Article 13 (transparency to deployers), Article 15 (accuracy
  / robustness / cybersecurity), or Article 72 (post-market monitoring).
- Does **not** claim Article 40 presumption of conformity.
- Does **not** claim Perplexity AI, Inc. endorsement or affiliation.
- Does **not** fetch, archive, or validate the cited URLs. The deployer
  must preserve the citation list (and, if pursuing source archival, the
  page snapshots) so the citation hash can be independently re-computed.
- Does **not** judge whether a given output is "public-interest text" —
  that determination is the deployer's, captured in their content policy.
- Provides the **Article 50 evidence layer only** for users of Perplexity
  AI via the OpenAI-compatible API.

## Known limitations (v0.1)

- Ephemeral in-process Ed25519 keys only. HSM-backed signing (AWS KMS,
  GCP KMS, Azure Key Vault, YubiHSM2) lands in v0.2.
- Perplexity may evolve the response shape (e.g. structured citation
  objects with titles + snippets in addition to URLs); the adapter
  currently hashes URLs only and ignores any structured citation
  metadata. A structured-citation variant of the schema lands in v0.2.
- Citation extraction is best-effort across SDK shapes (`response.citations`,
  `response.model_extra["citations"]`, dict-shaped responses). If
  Perplexity introduces a third surface, file an issue.
- No built-in source-page archival. If a regulator asks "what did URL X
  actually say at the time of inference?" the deployer must operate a
  separate snapshot pipeline.

## Roadmap

- v0.2: Structured-citation schema (URL + title + snippet hash).
- v0.2: Pluggable HSM-backed signer.
- v0.3: Built-in Merkle batcher with periodic flush to anchoring service.
- v0.3: Optional integration hook for source-archival (e.g. WARC).

## License

Apache 2.0. See `LICENSE`.
