"""Article 50(4) public-interest text labelling, with citation provenance.

Scenario: an EU news/media deployer uses Perplexity Sonar to draft a
public-facing summary on a matter of public interest. The published text
will carry an "AI-generated" disclosure label, and a human editor has
reviewed the output. The signed receipt records:

  - the prompt hash,
  - the assistant response hash,
  - the deterministic hash of the citation URL list Perplexity returned,
  - the disclosure-label and editorial-review attestations,
  - a subject-category tag for receipt-warehouse filtering.

Requires `PPLX_API_KEY`.

    pip install ledgerproof-perplexity
    export PPLX_API_KEY=pplx-...
    python examples/02_public_interest_with_citations.py
"""

from __future__ import annotations

from ledgerproof_perplexity import LedgerProofPerplexity


def main() -> None:
    client = LedgerProofPerplexity(
        deployer_id="urn:eu:deployer:acme-media-de",
        regulatory_context={
            # Article 50(4) — text disseminated to inform the public on
            # matters of public interest.
            "schema": "public_interest_text/v1",
            "jurisdiction": "EU",
            # Attestations about the publication surface:
            "disclosure_label_shown": True,  # we render an AI-generated label
            "editorial_review": True,        # human editor reviewed before publish
            "subject_category": "news.civic",
        },
    )

    resp = client.chat.completions.create(
        model="sonar-pro",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a research assistant for an EU newsroom. "
                    "Produce a short, neutral summary with inline citations."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Summarise the current state of EU AI Act Article 50 "
                    "enforcement guidance from the EU AI Office."
                ),
            },
        ],
    )

    print("--- AI-generated summary (display with 'AI-generated' label) ---")
    print(resp.choices[0].message.content)

    cites = getattr(resp, "citations", None) or []
    print(f"\n--- {len(cites)} citation(s) bound into the receipt ---")
    for url in cites:
        print(f"  - {url}")

    print(
        "\nA signed Article 50(4) receipt has been emitted to stdout — "
        "the citation hash binds this answer to the source list."
    )


if __name__ == "__main__":
    main()
