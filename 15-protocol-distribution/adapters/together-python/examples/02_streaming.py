"""
Streaming example: receipts finalize when the stream ends.

The text deltas are hashed incrementally as they arrive (C6); we never buffer
the full body. If the consumer breaks out of the loop early, calling
stream.close() will still emit a receipt covering whatever was streamed.
"""

from __future__ import annotations

import os

from ledgerproof_together import (
    LedgerProofTogether,
    RegulatoryContext,
    StderrEmitter,
)


def main() -> None:
    client = LedgerProofTogether(
        deployer_id="acme-corp-eu",
        api_key=os.environ.get("TOGETHER_API_KEY"),
        emitter=StderrEmitter(),
        regulatory_context=RegulatoryContext(
            article_50_paragraph="1",
            deployer_jurisdiction="FR",
            end_user_disclosure_made=True,
        ),
    )

    stream = client.chat.completions.create(
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        messages=[
            {"role": "user", "content": "Stream me a haiku about Bitcoin."},
        ],
        stream=True,
    )

    print("---- Streaming assistant reply ----")
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            print(delta, end="", flush=True)
    print()
    print("---- (A signed streaming receipt was emitted on stderr) ----")


if __name__ == "__main__":
    main()
