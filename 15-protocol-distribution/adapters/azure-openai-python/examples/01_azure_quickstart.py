"""01 — Quickstart: wrap the standard AzureOpenAI client.

Discipline reminders:
  - The Azure OpenAI response is returned unmodified (C7).
  - Receipts go to stdout via the default LogEmitter; swap for a
    WebhookEmitter or queue-backed emitter in production.
  - This adapter is NOT endorsed by Microsoft or Microsoft Azure.
  - This adapter does NOT confer Article 40 presumption of conformity.

Run:
    export AZURE_OPENAI_API_KEY=...
    export AZURE_OPENAI_ENDPOINT=https://contoso-weu.openai.azure.com/
    python examples/01_azure_quickstart.py
"""

from __future__ import annotations

import os

from ledgerproof_azure_openai import LedgerProofAzureOpenAI


def main() -> None:
    endpoint = os.environ.get(
        "AZURE_OPENAI_ENDPOINT", "https://contoso-weu.openai.azure.com/"
    )
    api_key = os.environ.get("AZURE_OPENAI_API_KEY", "dummy-key-for-dry-run")
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt4-prod")

    client = LedgerProofAzureOpenAI(
        deployer_id="urn:eu:deployer:contoso-bank",
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version="2024-08-01-preview",
        regulatory_context={
            "schema": "chatbot_session/v1",
            "jurisdiction": "EU",
        },
    )

    response = client.chat.completions.create(
        model=deployment,  # NB: in Azure, `model` is the deployment name.
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello to Frankfurt in one sentence."},
        ],
    )

    # `response` is the standard openai.types.chat.ChatCompletion — unchanged.
    print("---")
    print("Assistant:", response.choices[0].message.content)
    print("---")
    print("(A signed receipt was emitted to stdout above.)")


if __name__ == "__main__":
    main()
