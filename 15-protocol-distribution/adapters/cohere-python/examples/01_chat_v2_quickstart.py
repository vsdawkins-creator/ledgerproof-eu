"""
Quickstart: vanilla Cohere ClientV2.chat() with LedgerProof transparency receipts.

Run:
    export COHERE_API_KEY=...
    python examples/01_chat_v2_quickstart.py
"""

from __future__ import annotations

import os

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

    client = LedgerProofCohere(
        deployer_id="acme-corp-eu",
        api_key=api_key,
        signer=Ed25519Signer(),
        emitter=LogEmitter(),  # JSON-encoded receipts to stdout/logger
        regulatory_context=RegulatoryContext(
            article_50_paragraph="1",
            deployer_jurisdiction="DE",
            end_user_disclosure_made=True,
        ),
    )

    response = client.chat(
        model="command-a-03-2025",
        messages=[
            {"role": "user", "content": "Give me a one-sentence summary of GDPR's lawful bases."},
        ],
    )

    # C7: response is the original Cohere ChatResponse — adapter does not mutate it.
    print(response.message.content[0].text)


if __name__ == "__main__":
    main()
