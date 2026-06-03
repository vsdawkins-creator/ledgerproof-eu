"""Streaming example.

For streaming completions the adapter does NOT buffer the response body
(constraint C6). Instead, each chunk's incremental content updates an
in-memory SHA-256 hasher. When the stream is fully drained, a single receipt
is emitted whose `response_sha256` covers the full reconstructed text.

For `deepseek-reasoner` streaming, the reasoning trace is also hashed
incrementally on a separate hasher, so the trace binding remains verifiable
without ever materializing the trace in memory.

    pip install ledgerproof-deepseek
    export DEEPSEEK_API_KEY=sk-...
    python examples/03_streaming.py
"""

from __future__ import annotations

from ledgerproof_deepseek import LedgerProofDeepSeek


def main() -> None:
    client = LedgerProofDeepSeek(
        deployer_id="urn:eu:deployer:acme-bank-de",
        regulatory_context={"schema": "chatbot_session/v1", "jurisdiction": "EU"},
    )

    stream = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": "Count from 1 to 5, one word per line."}
        ],
        stream=True,
    )

    print("--- streamed response ---")
    for chunk in stream:
        for choice in chunk.choices:
            delta = choice.delta
            content = getattr(delta, "content", None)
            if content:
                print(content, end="", flush=True)
    print()
    print(
        "--- signed receipt emitted (response_sha256 covers the full "
        "reconstructed stream, computed incrementally per C6)."
    )


if __name__ == "__main__":
    main()
