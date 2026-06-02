"""
Quickstart: wrap an Anthropic client, send a message, see a receipt on stderr.

Requires:  pip install ledgerproof-anthropic
           export ANTHROPIC_API_KEY=sk-ant-...
"""

from __future__ import annotations

from ledgerproof_anthropic import (
    LedgerProofAnthropic,
    RegulatoryContext,
    StderrEmitter,
)


def main() -> None:
    client = LedgerProofAnthropic(
        deployer_id="acme-corp-eu",
        emitter=StderrEmitter(),
        regulatory_context=RegulatoryContext(
            article_50_paragraph="1",
            deployer_jurisdiction="DE",
            end_user_disclosure_made=True,
            notes="Customer support chatbot. End-user disclosure shown in UI banner.",
        ),
    )

    response = client.messages.create(
        model="claude-opus-4-1",
        max_tokens=256,
        messages=[
            {"role": "user", "content": "In one sentence: what is the EU AI Act?"}
        ],
    )

    # The response is the standard Anthropic Message — unchanged (C7).
    print("---- Assistant reply ----")
    print(response.content[0].text)
    print("---- (A signed receipt was emitted on stderr) ----")


if __name__ == "__main__":
    main()
