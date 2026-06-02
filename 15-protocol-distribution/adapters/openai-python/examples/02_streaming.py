"""Streaming example.

The wrapper signs the full reconstructed text via an incremental SHA-256
that is updated chunk-by-chunk (constraint C6). The receipt is emitted
once the stream is fully drained.
"""

from __future__ import annotations

from ledgerproof_openai import LedgerProofOpenAI


def main() -> None:
    client = LedgerProofOpenAI(
        deployer_id="urn:eu:deployer:acme-bank-de",
        regulatory_context={"schema": "chatbot_session/v1"},
    )

    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Stream a haiku about banking."}],
        stream=True,
    )

    print("--- streaming response ---")
    for chunk in stream:
        for choice in chunk.choices:
            delta = getattr(choice.delta, "content", None)
            if delta:
                print(delta, end="", flush=True)
    print("\n--- receipt emitted after stream drained ---")


if __name__ == "__main__":
    main()
