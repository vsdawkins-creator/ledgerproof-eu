"""
Streaming example. The adapter signs an incremental SHA-256 over text deltas (C6)
and emits a single receipt when the stream completes.
"""

from __future__ import annotations

from ledgerproof_anthropic import LedgerProofAnthropic, StderrEmitter


def main() -> None:
    client = LedgerProofAnthropic(
        deployer_id="acme-corp-eu",
        emitter=StderrEmitter(),
    )

    with client.messages.stream(
        model="claude-opus-4-1",
        max_tokens=512,
        messages=[
            {"role": "user", "content": "Count from 1 to 5 in English, one number per line."}
        ],
    ) as stream:
        print("---- Streaming reply ----")
        for delta in stream.text_stream:
            print(delta, end="", flush=True)
        print()

    print("---- (A signed receipt for the full stream was emitted on stderr) ----")


if __name__ == "__main__":
    main()
