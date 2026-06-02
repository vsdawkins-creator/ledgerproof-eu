"""
Streaming example: incremental SHA-256 over text deltas (constraint C6).

We NEVER buffer the full response body — the hasher is updated chunk-by-chunk
as Mistral streams the assistant message.
"""

from __future__ import annotations

import os

from ledgerproof_mistral import LedgerProofMistral, StderrEmitter


def main() -> None:
    client = LedgerProofMistral(
        deployer_id="acme-corp-eu",
        api_key=os.environ["MISTRAL_API_KEY"],
        emitter=StderrEmitter(),
    )

    print("---- Assistant reply (streaming) ----")
    stream = client.chat.stream(
        model="mistral-large-latest",
        messages=[
            {"role": "user", "content": "Write a haiku about cryptographic transparency."},
        ],
    )

    for chunk in stream:
        delta = chunk.data.choices[0].delta.content
        if delta:
            print(delta, end="", flush=True)
    print()
    print("---- (A signed receipt was emitted on stderr after the stream finished) ----")


if __name__ == "__main__":
    main()
