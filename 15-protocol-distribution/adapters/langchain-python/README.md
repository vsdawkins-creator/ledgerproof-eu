# ledgerproof-langchain

LangChain and LangGraph adapter for the LedgerProof protocol. Emits cryptographically
signed transparency receipts as a side channel, suitable for evidence of EU AI Act
Article 50 disclosure obligations.

## Install

```bash
pip install ledgerproof-langchain
# Optional LangGraph support:
pip install "ledgerproof-langchain[langgraph]"
```

Python 3.10+.

## 5-minute quickstart (callback handler)

```python
from langchain_openai import ChatOpenAI
from langchain_ledgerproof import LedgerProofCallbackHandler, LogEmitter

handler = LedgerProofCallbackHandler(
    deployer_id="acme-corp-eu",
    schema="chatbot_session/v1",
    emitter=LogEmitter("./receipts.jsonl"),
)

llm = ChatOpenAI(model="gpt-4o-mini", callbacks=[handler])
llm.invoke("Hello, are you an AI?")
# Receipt appended to ./receipts.jsonl. LLM response is not modified.
```

See `examples/01_chatbot_quickstart.py` and `examples/02_langgraph_editorial.py`.

## What this adapter does

- Captures a stream-aware SHA-256 transcript hash of the LLM interaction
  (commit-on-start, sign-on-end — never buffers the full body).
- Signs the receipt with Ed25519.
- Emits the receipt via a pluggable side channel (file, webhook, in-process queue).
- Validates receipt structure against one of three Pydantic schemas:
  - `chatbot_session/v1` (Article 50(1) — AI interaction disclosure)
  - `generated_content/v1` (Article 50(2) — AI-generated content marking)
  - `human_review/v1` (Article 50(4) — editorial-control exemption)
- Supports both legacy LangChain callbacks and LangGraph node middleware.

## What this adapter explicitly does NOT do

- Does not modify the LLM response payload. Receipts are side-channel only.
- Does not phone home during verification. Verification is offline against the
  Bitcoin chain and the published protocol public key.
- Does not provide Article 9 (risk management), Article 10 (data governance),
  Article 13 (transparency to users beyond Article 50), Article 15 (accuracy /
  robustness / cybersecurity), or Article 72 (post-market monitoring) coverage.
- Does not claim regulator endorsement.
- Does not claim Article 40 presumption of conformity (no harmonized standard
  has been published for Article 50 at the time of this release).
- Provides an Article 50 transparency receipt evidence layer only.

## Schemas

All three schemas reject email-shaped strings in `deployer_id`, `reviewer_role`,
and `review_rationale` fields as a GDPR safety check. Receipts should reference
opaque pseudonymous identifiers, not personal data.

## Phase 2+ roadmap

The MVP signer generates an ephemeral in-memory Ed25519 keypair. Production
deployments will use HSM-backed signing (AWS KMS, GCP Cloud KMS, Azure Key Vault,
YubiHSM). See `signer.py` for backend stubs.

## License

Apache 2.0. See `LICENSE`.
