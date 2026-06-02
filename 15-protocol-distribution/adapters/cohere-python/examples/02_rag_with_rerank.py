"""
RAG with Cohere Embed + Rerank + grounded chat — emits a rag_response/v1 receipt
that binds the SHA-256 of every retrieved document and its rerank relevance
score into the signed receipt.

Run:
    export COHERE_API_KEY=...
    python examples/02_rag_with_rerank.py
"""

from __future__ import annotations

import os

import cohere

from ledgerproof_cohere import (
    Ed25519Signer,
    LedgerProofCohere,
    LogEmitter,
    RegulatoryContext,
)


def main() -> None:
    api_key = os.environ.get("COHERE_API_KEY")
    if not api_key:
        raise SystemExit("Set COHERE_API_KEY to run this example.")

    # Use the raw Cohere client for Rerank (it's a side query, not a chat).
    raw_client = cohere.ClientV2(api_key=api_key)

    # Inject the LedgerProof wrapper over the same raw client for chat.
    client = LedgerProofCohere(
        deployer_id="acme-corp-eu",
        client=raw_client,
        signer=Ed25519Signer(),
        emitter=LogEmitter(),
        regulatory_context=RegulatoryContext(
            article_50_paragraph="1",
            deployer_jurisdiction="DE",
            end_user_disclosure_made=True,
            notes="Grounded answer over internal compliance KB",
        ),
    )

    # 1. Pretend these came out of your Embed + ANN retrieval step.
    candidate_docs = [
        {
            "id": "policy-001",
            "text": "Article 50(1) requires providers ensure AI systems intended to interact "
                    "directly with natural persons are designed so the persons concerned are "
                    "informed they are interacting with an AI system.",
            "source_uri": "internal://policy/eu-ai-act/article-50",
        },
        {
            "id": "policy-002",
            "text": "Article 50(2) requires providers of AI systems generating synthetic audio, "
                    "image, video or text content to mark outputs as artificially generated.",
            "source_uri": "internal://policy/eu-ai-act/article-50-2",
        },
        {
            "id": "policy-003",
            "text": "GDPR Article 6 enumerates the six lawful bases for processing personal data.",
            "source_uri": "internal://policy/gdpr/article-6",
        },
    ]

    # 2. Rerank with Cohere Rerank.
    query = "What does Article 50(1) require?"
    rerank_response = raw_client.rerank(
        model="rerank-v3.5",
        query=query,
        documents=[d["text"] for d in candidate_docs],
        top_n=2,
    )

    # 3. Use the top-N reranked docs as the grounded context.
    top_docs = [candidate_docs[r.index] for r in rerank_response.results]

    response = client.chat_with_retrieved_documents(
        documents=top_docs,
        rerank_results=rerank_response.results,
        model="command-a-03-2025",
        messages=[{"role": "user", "content": query}],
    )

    print(response.message.content[0].text)
    # The receipt emitted to LogEmitter has schema == "rag_response/v1" and
    # retrieved_documents[*].sha256_hex bound into the signature.


if __name__ == "__main__":
    main()
