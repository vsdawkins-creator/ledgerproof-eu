# ledgerproof-snowflake-cortex

LedgerProof adapter for [Snowflake Cortex](https://www.snowflake.com/en/data-cloud/cortex/) — the in-warehouse LLM and AI-services surface running over enterprise data in Snowflake. Emits side-channel cryptographic transparency receipts for AI inference calls, intended to support deployers preparing for EU AI Act Article 50 obligations (applicable from 2 August 2026).

This adapter is purpose-built for the Cortex usage pattern where the data being reasoned over is governed inside an enterprise data warehouse — adding warehouse / database / schema / table-level lineage attribution to the receipt so a Cortex Search Service or Cortex SQL RAG flow can be audited end-to-end.

## Important disclaimers

- **C1 — No regulator endorsement.** LedgerProof is an open cryptographic protocol stewarded by the LedgerProof Foundation. It has not been endorsed by the European Commission, the EU AI Office, any national supervisory authority, or any standardisation body. It does not, on its own, satisfy Article 50 — that determination is made by deployers, their counsel, and ultimately by regulators.
- **C1 — No Article 40 presumption of conformity.** LedgerProof is not a harmonised standard and does not confer a presumption of conformity under Article 40 of the EU AI Act.
- **Not endorsed by Snowflake.** This adapter is an independent open-source project. It is not produced, sponsored, endorsed, or supported by Snowflake Inc. "Snowflake", "Snowflake Cortex", "Cortex Search Service", and "Snowpark" are trademarks of Snowflake Inc., used here nominatively to describe interoperability.
- **C7 — Side-channel only.** Receipts are emitted asynchronously and never alter, delay, or proxy `Complete`, `Summarize`, `Translate`, `ExtractAnswer`, `Sentiment`, or Cortex Search Service responses returned by Snowflake.
- **C6 — Stream-aware signing.** For any streamed completion path, receipts are emitted once after the stream terminates, over the concatenated output.
- **C4 — Local verification only.** Receipts can be verified offline against the public key. No verification endpoint is operated by the Foundation in Phase 1.

## Why Snowflake Cortex specifically

Snowflake Cortex is the LLM surface that runs *inside* the customer's data warehouse — the most regulated, governed, auditable place AI inference can happen in an enterprise. That means:

- The data feeding the model has documented lineage: warehouse → database → schema → table.
- Article 50(2) "synthetic content" attribution can be tied back to the exact governed dataset that produced it.
- Article 50(1) chatbot interactions over enterprise data (Cortex Search Service RAG) can carry the *Snowflake-side* source attribution into the transparency receipt without exposing the underlying rows.

This adapter ships two extra receipt schemas — `enterprise_data_lineage/v1` and `cortex_search_rag/v1` — that capture exactly that Snowflake-native attribution surface.

## Installation

```bash
pip install ledgerproof-snowflake-cortex
```

## Quickstart

```python
from snowflake.snowpark import Session
from ledgerproof_snowflake_cortex import LedgerProofCortex

session = Session.builder.configs({
    "account": "...",
    "user": "...",
    "password": "...",
    "role": "...",
    "warehouse": "COMPUTE_WH",
    "database": "AI_APP",
    "schema": "PUBLIC",
}).create()

cortex = LedgerProofCortex(
    session=session,
    lpr_signing_key_path="key.pem",   # Ed25519 private key (PEM)
    lpr_deployer_id="deployer-123",
)

answer = cortex.complete(
    model="llama3.1-70b",
    prompt="Summarise our Q3 risk register.",
    lpr_schema="chatbot_session/v1",
    lpr_subject_id_hash="sha256:...",  # pseudonymous subject id
)
print(answer)
# Receipt has been emitted via side-channel.
```

### Enterprise data-warehouse lineage attribution (Article 50(2))

When Cortex generates content from governed warehouse data, the
`enterprise_data_lineage/v1` schema captures the upstream source surface
(warehouse + database + schema + table) so the synthetic content can be traced
back to its governed inputs without leaking the rows themselves.

```python
cortex.complete(
    model="claude-3-5-sonnet",
    prompt="Draft a customer-facing summary of this account.",
    lpr_schema="enterprise_data_lineage/v1",
    lpr_warehouse="COMPUTE_WH",
    lpr_source_database="CRM_PROD",
    lpr_source_schema="ACCOUNTS",
    lpr_source_tables=["CUSTOMER_360", "INTERACTION_LOG"],
)
```

### Cortex Search Service RAG (Article 50(1))

For a retrieval-augmented chatbot grounded in a Cortex Search Service, the
`cortex_search_rag/v1` schema captures the Search Service identifier and the
hashed retrieval fingerprint so a regulator-facing audit can reconstruct *which*
governed corpus produced a given answer.

```python
from ledgerproof_snowflake_cortex import LedgerProofCortexSearch

search = LedgerProofCortexSearch(
    session=session,
    lpr_signing_key_path="key.pem",
    lpr_deployer_id="deployer-123",
)

result = search.query(
    service_name="AI_APP.PUBLIC.SUPPORT_KB",
    query="How do I rotate the data masking policy?",
    columns=["CHUNK", "SOURCE_URL"],
    limit=5,
    lpr_subject_id_hash="sha256:...",
)
```

## Supported receipt schemas

| Schema | Article 50 hook | Use case |
|---|---|---|
| `chatbot_session/v1` | 50(1) | Conversational chatbots backed by Cortex `Complete` |
| `generated_content/v1` | 50(2) | Generic Cortex text generation, summaries, translations |
| `enterprise_data_lineage/v1` | 50(2) variant | Synthetic content with warehouse + database + schema + table-source attribution |
| `cortex_search_rag/v1` | 50(1) variant | Chatbot answers grounded in a Cortex Search Service |

## Supported Cortex surfaces

The adapter wraps the public Snowflake Cortex Python surface:

- `snowflake.cortex.Complete` — chat completion (sync + chat-messages)
- `snowflake.cortex.Summarize`
- `snowflake.cortex.Translate`
- `snowflake.cortex.ExtractAnswer`
- `snowflake.cortex.Sentiment`
- Cortex Search Service queries

Models known to the public Cortex surface include `llama3.1-70b`,
`snowflake-arctic`, `mistral-large`, `claude-3-5-sonnet`, `gemma-7b`, and
`mixtral-8x7b`. The adapter does not pin a model list; whatever Cortex
accepts, the wrapper forwards.

## GDPR notes

The adapter validates that fields commonly carrying personal data (prompts,
completions, subject identifiers) are either omitted, hashed, or pseudonymised
before being included in a receipt. Deployers remain controllers under GDPR.
For warehouse-grounded flows, the adapter records *table identifiers* — never
row content — so the receipt itself does not become a data-protection liability.

## License

Apache 2.0. See [LICENSE](LICENSE).
