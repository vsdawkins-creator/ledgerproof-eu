"""Quickstart: wrap OpenAI client, make a chat call, see receipt emitted.

Requires the `OPENAI_API_KEY` environment variable.

    pip install ledgerproof-openai
    export OPENAI_API_KEY=sk-...
    python examples/01_chat_completion_quickstart.py
"""

from __future__ import annotations

from ledgerproof_openai import LedgerProofOpenAI


def main() -> None:
    client = LedgerProofOpenAI(
        deployer_id="urn:eu:deployer:acme-bank-de",
        regulatory_context={
            "schema": "chatbot_session/v1",
            "jurisdiction": "EU",
        },
    )

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
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
