"""
Quickstart: wrap AI21Client and emit an Article 50 receipt for a Jamba chat call.

Run:
    export AI21_API_KEY=...
    python examples/01_jamba_quickstart.py
"""

from __future__ import annotations

from ledgerproof_ai21 import (
    LedgerProofAI21,
    LogEmitter,
    RegulatoryContext,
)


def main() -> None:
    client = LedgerProofAI21(
        deployer_id="acme-corp-eu",
        emitter=LogEmitter(),  # signed receipt printed to stdout / logger
        regulatory_context=RegulatoryContext(
            article_50_paragraph="1",
            deployer_jurisdiction="EU",
            end_user_disclosure_made=True,
            notes="Customer-facing chatbot powered by Jamba 1.5 Large.",
        ),
        # API key picked up from AI21_API_KEY by the underlying SDK.
    )

    response = client.chat.completions.create(
        model="jamba-1.5-large",
        messages=[
            {"role": "system", "content": "You are a helpful EU compliance assistant."},
            {"role": "user", "content": "What does Article 50 of the EU AI Act require?"},
        ],
    )

    print("Assistant:", response.choices[0].message.content)
    # A signed receipt was emitted on the side channel BEFORE we returned.


if __name__ == "__main__":
    main()
