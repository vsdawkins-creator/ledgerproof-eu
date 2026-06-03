"""
Image generation example: FLUX on Fireworks with an Article 50(2) receipt.

The receipt is a `flux_image_generation/v1`, capturing:
  - SHA-256 of the prompt text
  - SHA-256 of each returned image
  - Open-model attribution (Black Forest Labs builds FLUX; Fireworks hosts)
"""

from __future__ import annotations

import os

from ledgerproof_fireworks import (
    LedgerProofFireworks,
    OpenModelAttribution,
    RegulatoryContext,
    StderrEmitter,
)


def main() -> None:
    client = LedgerProofFireworks(
        deployer_id="acme-creative-eu",
        api_key=os.environ.get("FIREWORKS_API_KEY"),
        emitter=StderrEmitter(),
        schema="flux_image_generation/v1",
        regulatory_context=RegulatoryContext(
            article_50_paragraph="2",  # synthetic content
            deployer_jurisdiction="DE",
            end_user_disclosure_made=True,
            notes="Stock image generator. Each output is watermarked + receipt-signed.",
        ),
        open_model=OpenModelAttribution(
            underlying_model_family="flux",
            underlying_model_provider="black-forest-labs",
            host_provider="fireworks",
            model_license="flux-1-schnell-apache-2.0",
        ),
    )

    response = client.image.generate(
        model="accounts/fireworks/models/flux-1-schnell-fp8",
        prompt="A photograph of an alpine lake at sunrise, soft pastel light.",
    )

    print("---- Image generation complete ----")
    if hasattr(response, "image"):
        print(f"Image object: {type(response.image).__name__}")
    print("---- (A signed flux_image_generation/v1 receipt was emitted on stderr) ----")


if __name__ == "__main__":
    main()
