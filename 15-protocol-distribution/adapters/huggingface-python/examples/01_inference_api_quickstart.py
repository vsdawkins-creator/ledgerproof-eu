"""5-minute quickstart — Hugging Face Inference API with LedgerProof receipts.

Runs against the hosted Hugging Face Inference API. Set HF_TOKEN in your env.
The signed Article 50 receipt is emitted to stdout (LogEmitter).

NOTE: This adapter is not endorsed by Hugging Face, the European Commission,
the EU AI Office, or any national supervisory authority. It does not claim
Article 40 presumption of conformity.
"""

from __future__ import annotations

import os

from ledgerproof_huggingface import LedgerProofInferenceClient


def main() -> None:
    client = LedgerProofInferenceClient(
        deployer_id="urn:eu:deployer:acme-bank-de",
        # eu_open_model_hosted/v1 records the Hugging Face hosting + open-model
        # attribution — strategic for deployers building on EU AI sovereignty.
        regulatory_context={
            "schema": "eu_open_model_hosted/v1",
            "jurisdiction": "EU",
            "model_license": "llama-3.1-community-license",
            "open_weights": True,
        },
        model="meta-llama/Llama-3.1-70B-Instruct",
        token=os.environ.get("HF_TOKEN"),
    )

    resp = client.chat_completion(
        messages=[
            {"role": "system", "content": "You are a concise assistant."},
            {"role": "user", "content": "What is the capital of France?"},
        ],
        max_tokens=64,
    )

    print("\n--- Model output ---")
    print(resp.choices[0].message.content)
    print("--- (signed receipt was emitted above as a JSON line) ---\n")


if __name__ == "__main__":
    main()
