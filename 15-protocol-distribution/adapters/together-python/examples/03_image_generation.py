"""
Image generation example: FLUX on Together with an Article 50(2) receipt.

The receipt is a `image_generation/v1`, captures:
  - SHA-256 of the prompt text
  - SHA-256 of each returned image (where bytes are inline as b64_json)
  - Open-model attribution (Black Forest Labs builds FLUX; Together hosts)
"""

from __future__ import annotations

import os

from ledgerproof_together import (
    LedgerProofTogether,
    OpenModelAttribution,
    RegulatoryContext,
    StderrEmitter,
)


def main() -> None:
    client = LedgerProofTogether(
        deployer_id="acme-creative-eu",
        api_key=os.environ.get("TOGETHER_API_KEY"),
        emitter=StderrEmitter(),
        schema="image_generation/v1",
        regulatory_context=RegulatoryContext(
            article_50_paragraph="2",  # synthetic content
            deployer_jurisdiction="DE",
            end_user_disclosure_made=True,
            notes="Stock image generator. Each output is watermarked + receipt-signed.",
        ),
        open_model=OpenModelAttribution(
            underlying_model_family="flux",
            underlying_model_provider="black-forest-labs",
            host_provider="together",
            model_license="flux-1-schnell-apache-2.0",
        ),
    )

    response = client.images.generate(
        model="black-forest-labs/FLUX.1-schnell-Free",
        prompt="A photograph of an alpine lake at sunrise, soft pastel light.",
        width=1024,
        height=1024,
        steps=4,
        n=1,
    )

    print("---- Image generation complete ----")
    if hasattr(response, "data") and response.data:
        first = response.data[0]
        url = getattr(first, "url", None)
        print(f"Image URL (if any): {url}")
    print("---- (A signed image_generation/v1 receipt was emitted on stderr) ----")


if __name__ == "__main__":
    main()
