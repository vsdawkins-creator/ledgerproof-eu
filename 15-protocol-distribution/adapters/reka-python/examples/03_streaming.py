"""
Streaming example: receipt is built from an incremental SHA-256 over text deltas (C6).

The response is yielded chunk-by-chunk; the receipt is emitted once the stream
finishes (or the iterator's __exit__ runs).

Requires:  pip install ledgerproof-reka
           export REKA_API_KEY=...
"""

from __future__ import annotations

from ledgerproof_reka import (
    LedgerProofReka,
    RegulatoryContext,
    StderrEmitter,
)


def main() -> None:
    client = LedgerProofReka(
        deployer_id="acme-corp-eu",
        emitter=StderrEmitter(),
        regulatory_context=RegulatoryContext(
            article_50_paragraph="1",
            deployer_jurisdiction="DE",
            end_user_disclosure_made=True,
        ),
    )

    print("---- Streaming reply ----")
    stream = client.chat.create_stream(
        model="reka-flash-3.1",
        messages=[
            {
                "role": "user",
                "content": "List three EU AI Act transparency obligations under Article 50.",
            }
        ],
    )
    for chunk in stream:
        # Reka exposes deltas under responses[0].chunk.content (SDK v3.x).
        try:
            delta = chunk.responses[0].chunk.content
        except (AttributeError, IndexError):
            delta = ""
        if delta:
            print(delta, end="", flush=True)
    print("\n---- (Signed streaming receipt emitted on stderr) ----")


if __name__ == "__main__":
    main()
