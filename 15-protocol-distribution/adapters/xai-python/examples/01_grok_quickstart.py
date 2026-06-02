"""Quickstart: wrap an OpenAI client pointed at xAI Grok, make a chat call,
see the signed Article 50 receipt emitted on stdout.

Requires the `XAI_API_KEY` environment variable.

    pip install ledgerproof-xai
    export XAI_API_KEY=xai-...
    python examples/01_grok_quickstart.py
"""

from __future__ import annotations

from ledgerproof_xai import LedgerProofXAI


def main() -> None:
    # The adapter defaults to base_url=https://api.x.ai/v1 and reads
    # XAI_API_KEY from the environment.
    client = LedgerProofXAI(
        deployer_id="urn:eu:deployer:acme-media-de",
        regulatory_context={
            "schema": "chatbot_session/v1",
            "jurisdiction": "EU",
        },
    )

    resp = client.chat.completions.create(
        model="grok-2-latest",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello in three languages."},
        ],
    )

    print("--- assistant response ---")
    print(resp.choices[0].message.content)
    print("--- signed receipt was emitted to stdout above ---")


if __name__ == "__main__":
    main()
