# langchain-ledgerproof

LangChain callback that auto-issues EU AI Act Article 50 receipts for every LLM call.

```bash
pip install langchain-ledgerproof
```

```python
from langchain_anthropic import ChatAnthropic
from langchain_ledgerproof import LedgerProofCallbackHandler

callback = LedgerProofCallbackHandler(
    publisher_id="LEI:5493001KJTIIGC8Y1R12",
    deployer_country="DE",
    deployer_name="Acme Corp",
)

llm = ChatAnthropic(model="claude-sonnet-4-6", callbacks=[callback])
response = llm.invoke("Write a haiku about Bitcoin.")
# Receipt issued automatically. Your code is now Article 50 compliant.
```

Works with any LangChain LLM (Chat or Completion). Each invocation in a chain
or agent gets its own receipt. Background issuance — your chain isn't blocked.

## Configuration

Reads `LEDGERPROOF_API_KEY` from the environment if not passed.

See the [main ledgerproof package](../python) for the full Article 50 protocol.

## License

Apache-2.0.
