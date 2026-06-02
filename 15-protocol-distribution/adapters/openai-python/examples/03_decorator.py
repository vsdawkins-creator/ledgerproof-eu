"""Using @lpr_track to instrument an existing function without changing
the client class.
"""

from __future__ import annotations

from openai import OpenAI

from ledgerproof_openai import lpr_track


client = OpenAI()


@lpr_track(
    deployer_id="urn:eu:deployer:acme-bank-de",
    regulatory_context={"schema": "chatbot_session/v1"},
)
def ask(question: str, *, messages):
    return client.chat.completions.create(model="gpt-4o-mini", messages=messages)


def main() -> None:
    messages = [{"role": "user", "content": "What is SEPA?"}]
    resp = ask("What is SEPA?", messages=messages)
    print("--- assistant response ---")
    print(resp.choices[0].message.content)
    print("--- receipt emitted to stdout ---")


if __name__ == "__main__":
    main()
