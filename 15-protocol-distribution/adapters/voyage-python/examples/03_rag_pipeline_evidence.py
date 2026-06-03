"""
Full RAG pipeline: Voyage embed -> Voyage rerank -> downstream chatbot turn.

We emit three receipts:

    1. embedding_inference/v1   — supporting infrastructure, the embed call
    2. rerank_inference/v1      — supporting infrastructure, the rerank call
    3. rag_pipeline_evidence/v1 — Article 50(1) variant, stitches 1+2 to a
                                  downstream chatbot turn

The downstream chatbot turn here is a *stub* (a dict shaped like what
ledgerproof-openai / ledgerproof-anthropic / ledgerproof-cohere would emit). In
production you'd take the actual signed receipt returned from one of those
adapters.

Run:
    export VOYAGE_API_KEY=...
    python examples/03_rag_pipeline_evidence.py
"""

from __future__ import annotations

import hashlib
import json
import os

from ledgerproof_voyage import (
    Ed25519Signer,
    LedgerProofVoyage,
    QueueEmitter,
    emit_rag_pipeline_receipt,
)
from ledgerproof_voyage.canonical import canonical_encode


def _build_stub_downstream_receipt(
    deployer_id: str, user_query: str, assistant_response: str
) -> dict:
    """
    Pretend we ran ledgerproof-openai/anthropic/cohere and got back a signed
    receipt. In real code this comes from the actual chat adapter.
    """
    payload = {
        "schema": "chatbot_session/v1",
        "schema_version": 1,
        "receipt_id": "rcpt_chat_simulated",
        "deployer_id": deployer_id,
        "model": {
            "provider": "anthropic",
            "model_id": "claude-3-7-sonnet",
            "response_id": "msg_xyz",
        },
        "content_refs": [
            {
                "sha256_hex": hashlib.sha256(user_query.encode()).hexdigest(),
                "byte_length": len(user_query.encode()),
                "role": "user",
            },
            {
                "sha256_hex": hashlib.sha256(assistant_response.encode()).hexdigest(),
                "byte_length": len(assistant_response.encode()),
                "role": "assistant",
            },
        ],
    }
    return {
        "receipt": payload,
        "signature_alg": "ed25519",
        "signature_b64": "AAAA-stub",
        "signer_key_id": "lpr-ed25519-stub-downstream",
        "canonical_encoding": "cbor-rfc8949-deterministic",
    }


def main() -> None:
    captured_receipts: list = []
    signer = Ed25519Signer()
    deployer_id = "acme-corp-eu"

    client = LedgerProofVoyage(
        deployer_id=deployer_id,
        api_key=os.environ.get("VOYAGE_API_KEY"),
        signer=signer,
        emitter=QueueEmitter(captured_receipts.append),
    )

    # --- 1. Embed the candidate documents (would normally already be in your vector DB) ---
    documents = [
        "Article 50(1): natural persons must be informed they are interacting with an AI system.",
        "Article 50(5): disclosures must be in a language the recipient understands.",
        "Annex IV: technical documentation requirements for high-risk AI systems.",
    ]
    client.embed(
        texts=documents,
        model="voyage-3-large",
        input_type="document",
    )

    # --- 2. Rerank against the user query ---
    user_query = "Does my chatbot need to disclose it's AI?"
    client.rerank(
        query=user_query,
        documents=documents,
        model="rerank-2",
        top_k=2,
    )

    upstream_signed = list(captured_receipts)
    assert len(upstream_signed) == 2

    # --- 3. Pretend we ran a downstream chat adapter and got its signed receipt ---
    assistant_response = (
        "Yes. Under Article 50(1) of the EU AI Act, providers of AI systems "
        "intended to interact directly with natural persons must inform those "
        "persons that they are interacting with an AI system."
    )
    downstream_signed = _build_stub_downstream_receipt(
        deployer_id=deployer_id,
        user_query=user_query,
        assistant_response=assistant_response,
    )

    # --- 4. Stitch upstream + downstream via rag_pipeline_evidence/v1 ---
    rag_signed = emit_rag_pipeline_receipt(
        deployer_id=deployer_id,
        upstream_signed_receipts=upstream_signed,
        downstream_signed_receipt=downstream_signed,
        downstream_adapter="ledgerproof-anthropic",
        user_query=user_query,
        assistant_response=assistant_response,
        signer=signer,
        emitter=QueueEmitter(captured_receipts.append),
    )

    print("=== RAG pipeline evidence chain ===")
    print()
    print("(1) embedding_inference/v1 receipt:")
    print(f"    receipt_id = {upstream_signed[0]['receipt']['receipt_id']}")
    print(f"    canonical hash = {hashlib.sha256(canonical_encode(upstream_signed[0]['receipt'])).hexdigest()}")
    print()
    print("(2) rerank_inference/v1 receipt:")
    print(f"    receipt_id = {upstream_signed[1]['receipt']['receipt_id']}")
    print(f"    canonical hash = {hashlib.sha256(canonical_encode(upstream_signed[1]['receipt'])).hexdigest()}")
    print()
    print("(3) rag_pipeline_evidence/v1 receipt (Article 50(1)):")
    print(json.dumps(rag_signed["receipt"], indent=2, default=str))


if __name__ == "__main__":
    main()
