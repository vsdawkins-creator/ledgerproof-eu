"""
EU-sovereign AI attribution example.

Mistral is a French / EU-headquartered model provider. Deployers that need to
demonstrate EU residency / EU-operated infrastructure / EU jurisdiction can
attach an `EuSovereigntyAttestation` block to every receipt by switching to the
`eu_sovereign_ai_session/v1` schema.

Strategic context: Article 50 transparency receipts can co-evidence the GDPR
Schrems-II analysis and EU sovereignty messaging. The attestation block is
descriptive metadata, not a certification — see the C1 disclaimer in the README.
"""

from __future__ import annotations

import os

from ledgerproof_mistral import (
    EuSovereigntyAttestation,
    LedgerProofMistral,
    RegulatoryContext,
    StderrEmitter,
)


def main() -> None:
    eu_sov = EuSovereigntyAttestation(
        inference_region="eu-west-3",  # Paris
        eu_data_residency=True,
        eu_operated_infrastructure=True,
        provider_eu_headquartered=True,
        provider_legal_entity="Mistral AI SAS (Paris, France)",
        transfer_mechanism=None,  # No third-country transfer required.
    )

    client = LedgerProofMistral(
        deployer_id="acme-bank-eu",
        api_key=os.environ["MISTRAL_API_KEY"],
        emitter=StderrEmitter(),
        schema="eu_sovereign_ai_session/v1",
        regulatory_context=RegulatoryContext(
            article_50_paragraph="1",
            deployer_jurisdiction="DE",
            end_user_disclosure_made=True,
            notes="EU-only inference; no third-country transfer.",
        ),
        eu_sovereignty=eu_sov,
    )

    response = client.chat.complete(
        model="mistral-large-latest",
        messages=[
            {"role": "user", "content": "Summarise the Article 50 transparency obligation."},
        ],
    )

    print("---- Assistant reply ----")
    print(response.choices[0].message.content)
    print("---- (Signed receipt with EU-sovereignty attestation emitted on stderr) ----")


if __name__ == "__main__":
    main()
