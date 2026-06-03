"""
Quickstart: Voyage AI embed() with LedgerProof side-channel receipt.

Wraps `voyageai.Client` with `LedgerProofVoyage`. The Voyage EmbeddingsObject is
returned UNCHANGED. A signed embedding_inference/v1 receipt is emitted on the
side channel (here: a Python list via QueueEmitter — in production it would be
a webhook, SQS queue, Kafka topic, etc.).

Run:
    export VOYAGE_API_KEY=...
    python examples/01_voyage_embed_quickstart.py
"""

from __future__ import annotations

import json
import os

from ledgerproof_voyage import (
    Ed25519Signer,
    LedgerProofVoyage,
    QueueEmitter,
)


def main() -> None:
    captured_receipts: list = []
    signer = Ed25519Signer()

    client = LedgerProofVoyage(
        deployer_id="acme-corp-eu",
        api_key=os.environ.get("VOYAGE_API_KEY"),
        signer=signer,
        emitter=QueueEmitter(captured_receipts.append),
    )

    # The Voyage embed call is unmodified — same signature as voyageai.Client.embed.
    result = client.embed(
        texts=[
            "Article 50 of the EU AI Act establishes transparency obligations "
            "for providers and deployers of AI systems intended to interact "
            "directly with natural persons.",
            "Enforcement of Article 50 begins on 2 August 2026.",
        ],
        model="voyage-3-large",
        input_type="document",
    )

    print(f"Received {len(result.embeddings)} embedding vector(s).")
    print(f"First vector dim: {len(result.embeddings[0])}")
    print(f"Total tokens used: {result.total_tokens}")

    print()
    print("=== Signed LedgerProof receipt (side channel) ===")
    print(json.dumps(captured_receipts[0]["receipt"], indent=2, default=str))
    print()
    print(f"Signed by key: {captured_receipts[0]['signer_key_id']}")
    print(f"Public key (verify offline): {signer.public_key_b64()}")


if __name__ == "__main__":
    main()
