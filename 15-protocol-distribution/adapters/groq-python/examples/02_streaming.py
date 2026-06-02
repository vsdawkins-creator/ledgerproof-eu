"""Streaming demo — C6 stream-aware signing.

The receipt is emitted once after the stream terminates, over the
concatenated completion. The print loop runs at full Groq LPU speed.
"""

from ledgerproof_groq import LedgerProofGroq


def main() -> None:
    client = LedgerProofGroq(lpr_deployer_id="demo-deployer-001")

    stream = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Write a haiku about LPU latency."}],
        stream=True,
        lpr_schema="low_latency_inference/v1",
    )

    for ev in stream:
        delta = ev.choices[0].delta
        if getattr(delta, "content", None):
            print(delta.content, end="", flush=True)
    print()

    client.flush()
    client.close()


if __name__ == "__main__":
    main()
