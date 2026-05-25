"""The three-line Article 50 compliance demo.

  pip install ledgerproof openai
  export OPENAI_API_KEY=sk-...
  export LEDGERPROOF_API_KEY=lp_...
  python examples/01_minimal.py

Every OpenAI chat completion below issues an LPR receipt automatically,
Bitcoin-anchored, GDPR-safe, verifiable by anyone.
"""

import openai
import ledgerproof

client = openai.OpenAI()

ledgerproof.attach(
    client,
    publisher_id="LEI:5493001KJTIIGC8Y1R12",  # your legal-entity identifier
    deployer_country="DE",  # ISO 3166-1 alpha-2
    deployer_name="Acme Corp",
)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Write a haiku about Bitcoin."}],
)

print(response.choices[0].message.content)
print()

# The receipt is issued in the background. Await it if you want the URL.
future = getattr(response, "_ledgerproof_future", None)
if future is not None:
    receipt = future.result(timeout=10)
    if receipt is not None:
        print(f"LedgerProof receipt: {receipt.verify_url}")
