"""
Quickstart: wrap a Reka client, send a text message, see a receipt on stderr.

Requires:  pip install ledgerproof-reka
           export REKA_API_KEY=...
"""

from __future__ import annotations

from ledgerproof_reka import (
    LedgerProofReka,
    RegulatoryContext,
    StderrEmitter,
)


def main() -> None:
    client = LedgerProofReka(
        deployer_id="acme-corp-eu",
        emitter=StderrEmitter(),
        regulatory_context=RegulatoryContext(
            article_50_paragraph="1",
            deployer_jurisdiction="DE",
            end_user_disclosure_made=True,
            notes="Customer support chatbot. End-user disclosure shown in UI banner.",
        ),
    )

    response = client.chat.create(
        model="reka-flash-3.1",
        messages=[
            {
                "role": "user",
                "content": "In one sentence: what is the EU AI Act?",
            }
        ],
    )

    # The response is the standard Reka ChatResponse — unchanged (C7).
    print("---- Assistant reply ----")
    print(response.responses[0].message.content)
    print("---- (A signed receipt was emitted on stderr) ----")


if __name__ == "__main__":
    main()
