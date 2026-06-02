"""Article 50(4) editorial pipeline with human-in-the-loop review.

Scenario:
    A German newsroom (Spiegel-class) drafts news articles assisted by
    a Haystack LLM pipeline. EU AI Act Art. 50(4) obligates disclosure
    when AI-generated/manipulated text is published as news of public
    interest, UNLESS the content has undergone human editorial review.

    LedgerProof emits an `editorial_pipeline_review/v1` receipt that
    cryptographically attests the human-review decision so downstream
    auditors / regulators can verify the editorial workflow.

Run:
    python examples/03_editorial_pipeline.py
"""

from __future__ import annotations

from haystack import Pipeline, component

from ledgerproof_haystack import (
    FileEmitter,
    LedgerProofComponent,
    load_or_generate_signing_key,
)


@component
class StubDrafter:
    """Tiny stand-in for an LLM drafting component (no API key needed)."""

    @component.output_types(draft=str)
    def run(self, topic: str) -> dict:
        return {
            "draft": (
                f"Draft article on {topic}: Brussels regulators today "
                "announced new transparency guidance for AI deployers..."
            )
        }


@component
class HumanReviewGate:
    """Simulates a human editor sign-off."""

    @component.output_types(approved_text=str, reviewer=str, decision=str)
    def run(self, draft: str) -> dict:
        # In production: surface in CMS; capture editor ID + decision.
        return {
            "approved_text": draft + "\n\n[Reviewed by editorial desk]",
            "reviewer": "editor-mariana-k",
            "decision": "published",
        }


def main() -> None:
    key = load_or_generate_signing_key("./.lpr-newsroom.pem")
    emitter = FileEmitter("./audit/editorial-receipts/")

    pipeline = Pipeline()
    pipeline.add_component("drafter", StubDrafter())
    pipeline.add_component("reviewer", HumanReviewGate())
    pipeline.add_component(
        "ledgerproof",
        LedgerProofComponent(
            signing_key=key,
            schema="editorial_pipeline_review/v1",
            deployer="newsroom-de",
            emitter=emitter,
            extra_fields={
                "public_interest_category": "news",
                "human_editorial_review": True,
                "reviewer_id": "editor-mariana-k",
                "review_decision": "published",
                "pipeline_name": "spiegel-editorial",
            },
        ),
    )

    pipeline.connect("drafter.draft", "reviewer.draft")
    pipeline.connect("reviewer.approved_text", "ledgerproof.content")

    result = pipeline.run({
        "drafter": {"topic": "EU AI Act Article 50 enforcement"},
        "ledgerproof": {"query": "EU AI Act Article 50 enforcement"},
    })

    print("Published text:")
    print(result["reviewer"]["approved_text"])
    print()
    print("Editorial receipt id:", result["ledgerproof"]["receipt_id"])
    print("Receipts on disk under: ./audit/editorial-receipts/")


if __name__ == "__main__":
    main()
