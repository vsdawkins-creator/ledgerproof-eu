"""Low-latency streaming demo — C6 stream-aware signing.

The receipt is emitted once after the stream terminates, over the
concatenated completion. The print loop runs at full Cerebras wafer-scale
inference speed. The receipt is sealed with `wafer_scale_inference/v1`,
which captures `inference_latency_ms`, `tokens_per_second`, and the
`hardware_class` attribution.
"""

from ledgerproof_cerebras import LedgerProofCerebras


def main() -> None:
    client = LedgerProofCerebras(lpr_deployer_id="demo-deployer-001")

    stream = client.chat.completions.create(
        model="llama3.1-70b",
        messages=[{"role": "user", "content": "Write a haiku about wafer-scale inference."}],
        stream=True,
        lpr_schema="wafer_scale_inference/v1",
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
