"""Streaming chat_completion — receipt is emitted after the stream drains.

Stream-aware SHA-256 (constraint C6) means the receipt's response hash covers
the full reconstructed assistant text, not just the final chunk.
"""

from __future__ import annotations

import os

from ledgerproof_huggingface import LedgerProofInferenceClient


def main() -> None:
    client = LedgerProofInferenceClient(
        deployer_id="urn:eu:deployer:acme",
        regulatory_context={"schema": "chatbot_session/v1"},
        model="meta-llama/Llama-3.1-70B-Instruct",
        token=os.environ.get("HF_TOKEN"),
    )

    stream = client.chat_completion(
        messages=[{"role": "user", "content": "Write a haiku about Paris."}],
        max_tokens=80,
        stream=True,
    )

    print("\n--- Streaming output ---")
    for chunk in stream:
        try:
            delta = chunk.choices[0].delta.content
            if delta:
                print(delta, end="", flush=True)
        except (AttributeError, IndexError):
            continue
    print("\n--- (signed receipt was emitted above on drain) ---\n")


if __name__ == "__main__":
    main()
