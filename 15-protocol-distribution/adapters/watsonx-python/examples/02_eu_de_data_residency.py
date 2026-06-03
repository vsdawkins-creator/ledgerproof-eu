"""
EU-DE (Frankfurt) data-residency attestation for German enterprise.

Emits the `eu_data_residency/v1` receipt schema, which records:
  - attested region (eu-de)
  - watsonx project_id
  - tenant_id (deployer-supplied hash of IBM Cloud account)
  - cross-border transfer flag
  - SCC posture

Cross-checks attested region against the region parsed from Credentials.url
to catch drift between deployer claim and actual endpoint.

    python examples/02_eu_de_data_residency.py
"""

from __future__ import annotations

import logging
import os
import sys

from ledgerproof_watsonx import LedgerProofModelInference, StderrEmitter


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    try:
        from ibm_watsonx_ai import Credentials
    except ImportError:
        print("ibm-watsonx-ai not installed.")
        sys.exit(1)

    api_key = os.environ.get("WATSONX_API_KEY")
    project_id = os.environ.get("WATSONX_PROJECT_ID")
    if not api_key or not project_id:
        print("Set WATSONX_API_KEY and WATSONX_PROJECT_ID.")
        sys.exit(1)

    credentials = Credentials(
        url="https://eu-de.ml.cloud.ibm.com",
        api_key=api_key,
    )

    model = LedgerProofModelInference(
        deployer_id="acme-eu-bank",
        model_id="ibm/granite-3-8b-instruct",
        credentials=credentials,
        project_id=project_id,
        emitter=StderrEmitter(),
        attest_residency=True,
        sccs_in_place=True,
        tenant_id="acme-de-tenant-hash-redacted",
        regulatory_context={
            "article_50_paragraph": "1",
            "deployer_jurisdiction": "DE",
            "end_user_disclosure_made": True,
            "notes": "EU end-user; inference confined to eu-de.",
        },
    )

    response = model.chat(
        messages=[{"role": "user", "content": "Bonjour"}],
    )
    print("Assistant:", response["choices"][0]["message"]["content"])
    print(
        "\nReceipt emitted with schema=eu_data_residency/v1, "
        "attested_region=eu-de, eu_region=true, sccs_in_place=true."
    )


if __name__ == "__main__":
    main()
