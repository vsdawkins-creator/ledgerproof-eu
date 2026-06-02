"""
Long-context inference (Jamba 256k window) with `long_context_inference/v1`.

Demonstrates the dedicated Article 50(1) variant schema that records declared
and effective context-window utilization. Useful for RAG-over-corpus, multi-doc
legal review, code-review-of-whole-repo, and similar workloads where the 256k
context is the differentiator.

Run:
    export AI21_API_KEY=...
    python examples/02_long_context.py
"""

from __future__ import annotations

from ledgerproof_ai21 import (
    LedgerProofAI21,
    LogEmitter,
    LongContextAttestation,
    RegulatoryContext,
)


def main() -> None:
    # Pretend we're feeding 100 PDFs worth of context into Jamba.
    long_prompt = "Document {i} content...\n" * 5000

    client = LedgerProofAI21(
        deployer_id="acme-legaltech-eu",
        emitter=LogEmitter(),
        schema="long_context_inference/v1",
        regulatory_context=RegulatoryContext(
            article_50_paragraph="1",
            deployer_jurisdiction="EU",
            end_user_disclosure_made=True,
            notes="Multi-document legal review using Jamba's long-context window.",
        ),
        long_context=LongContextAttestation(
            declared_context_window=262_144,
            # Effective tokens normally come from the SDK's tokenizer; this is
            # a placeholder you would replace with the actual measured count.
            effective_input_tokens=len(long_prompt) // 4,
            long_context_workload="multi-doc-legal-review",
            truncation_applied=False,
        ),
    )

    response = client.chat.completions.create(
        model="jamba-1.5-large",
        messages=[
            {"role": "system", "content": "You are a legal review assistant."},
            {"role": "user", "content": long_prompt + "\nSummarise key risks."},
        ],
    )

    print("Assistant:", response.choices[0].message.content[:200], "...")
    # Signed long_context_inference/v1 receipt has been emitted on the side channel.


if __name__ == "__main__":
    main()
