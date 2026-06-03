"""
Voyage AI rerank() with LedgerProof side-channel receipt.

The receipt binds:
  - SHA-256 of the rerank query
  - SHA-256 of each candidate document (the actual byte content fed to Voyage)
  - the per-document relevance score
  - the post-rerank position
  - the original-list index Voyage reported

This is the cryptographic answer to "which documents got promoted, by how much,
and out of exactly what candidate set?" — the question every EU enterprise
auditor will ask post-2 August 2026 when investigating a RAG-pipeline incident.

Run:
    export VOYAGE_API_KEY=...
    python examples/02_voyage_rerank.py
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

    documents = [
        "Article 50(1): providers shall ensure that AI systems intended to interact directly with natural persons are designed and developed in such a way that the natural persons concerned are informed that they are interacting with an AI system.",
        "Annex IV of the EU AI Act: technical documentation requirements for high-risk AI systems.",
        "Recital 132: the transparency obligation in Article 50 is without prejudice to the obligations on providers and deployers of high-risk AI systems.",
        "GDPR Article 22: the data subject has the right not to be subject to a decision based solely on automated processing.",
    ]

    result = client.rerank(
        query="What does Article 50 require of chatbots?",
        documents=documents,
        model="rerank-2",
        top_k=3,
    )

    print("=== Voyage rerank results (returned unchanged) ===")
    for i, r in enumerate(result.results):
        print(f"  #{i}: original_index={r.index} score={r.relevance_score:.4f}")

    print()
    print("=== Signed LedgerProof receipt (side channel) ===")
    print(json.dumps(captured_receipts[0]["receipt"], indent=2, default=str))
    print()
    print(
        "Each rerank_results[].document_sha256_hex matches a SHA-256 of the "
        "exact bytes you fed in as documents[].  An auditor can later replay "
        "the candidate set, recompute the hashes, and confirm the model saw "
        "exactly these documents — and that the rerank scores recorded match."
    )


if __name__ == "__main__":
    main()
