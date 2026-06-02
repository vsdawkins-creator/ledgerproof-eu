"""
Streaming chat completion with incremental SHA-256 over text deltas.

Demonstrates constraint C6: stream-aware signing. The adapter never buffers
the full response body — it updates a streaming SHA-256 hash as chunks arrive,
then emits a single signed receipt when the stream finalizes.

This is the only viable strategy for Jamba 256k context streams, where the
output can run to tens of thousands of tokens.

Run:
    export AI21_API_KEY=...
    python examples/03_streaming.py
"""

from __future__ import annotations

from ledgerproof_ai21 import (
    JambaHybridAttestation,
    LedgerProofAI21,
    LogEmitter,
)


def main() -> None:
    client = LedgerProofAI21(
        deployer_id="acme-corp-eu",
        emitter=LogEmitter(),
        schema="jamba_hybrid_attribution/v1",
        jamba_hybrid=JambaHybridAttestation(
            architecture_family="mamba-transformer-hybrid",
            model_variant="jamba-1.5-large",
            parameter_class="398B-MoE",
            attention_layer_ratio="1:7",
        ),
    )

    stream = client.chat.completions.create(
        model="jamba-1.5-large",
        messages=[
            {"role": "user", "content": "Write a 3-paragraph summary of EU AI Act Article 50."},
        ],
        stream=True,
    )

    print("Assistant (streaming): ", end="", flush=True)
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            print(delta, end="", flush=True)
    print()
    # Signed jamba_hybrid_attribution/v1 receipt has been emitted with the
    # incremental SHA-256 of the full assistant text.


if __name__ == "__main__":
    main()
