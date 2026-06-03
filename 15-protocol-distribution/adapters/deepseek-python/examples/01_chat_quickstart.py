"""Quickstart: wrap an OpenAI client pointed at DeepSeek, make a chat call,
see the signed Article 50 receipt emitted on stdout.

Requires the `DEEPSEEK_API_KEY` environment variable.

    pip install ledgerproof-deepseek
    export DEEPSEEK_API_KEY=sk-...
    python examples/01_chat_quickstart.py
"""

from __future__ import annotations

from ledgerproof_deepseek import LedgerProofDeepSeek


def main() -> None:
    # The adapter defaults to base_url=https://api.deepseek.com and reads
    # DEEPSEEK_API_KEY from the environment.
    client = LedgerProofDeepSeek(
        deployer_id="urn:eu:deployer:acme-bank-de",
        regulatory_context={
            "schema": "chatbot_session/v1",
            "jurisdiction": "EU",
        },
    )

    resp = client.chat.completions.create(
        model="deepseek-chat",
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
