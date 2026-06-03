"""Quickstart: wrap an OpenAI client pointed at Perplexity AI, run a
Sonar search, and see a signed Article 50 receipt emitted on stdout.

Requires the `PPLX_API_KEY` environment variable.

    pip install ledgerproof-perplexity
    export PPLX_API_KEY=pplx-...
    python examples/01_perplexity_search_quickstart.py
"""

from __future__ import annotations

from ledgerproof_perplexity import LedgerProofPerplexity


def main() -> None:
    # Defaults: base_url=https://api.perplexity.ai, api_key=$PPLX_API_KEY.
    # For a basic chatbot session we use the chatbot_session/v1 schema.
    client = LedgerProofPerplexity(
        deployer_id="urn:eu:deployer:acme-media-de",
        regulatory_context={
            "schema": "chatbot_session/v1",
            "jurisdiction": "EU",
        },
    )

    resp = client.chat.completions.create(
        model="sonar",
        messages=[
            {"role": "system", "content": "You are a helpful research assistant."},
            {
                "role": "user",
                "content": "What is the EU AI Act Article 50 enforcement date?",
            },
        ],
    )

    print("--- assistant response ---")
    print(resp.choices[0].message.content)

    cites = getattr(resp, "citations", None) or []
    if cites:
        print("\n--- citations returned by Perplexity ---")
        for url in cites:
            print(f"  - {url}")

    print("\n--- signed receipt was emitted to stdout above ---")


if __name__ == "__main__":
    main()
