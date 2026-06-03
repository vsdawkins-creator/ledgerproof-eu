"""
IBM Granite open-weights attestation for Article 50 disclosure.

Granite 3.x is Apache-2.0 licensed and the weights are published on Hugging
Face. Emits the `granite_open_model/v1` receipt schema with an
OpenWeightsAttestation that records:
  - model_family: ibm-granite
  - license_spdx: Apache-2.0
  - weights_url: HF URL (auto-derived from model_id)
  - reproducible: True

This materially strengthens the deployer's Article 50 disclosure posture: the
underlying model is independently auditable and reproducible in a way that
closed-weights API calls are not.

    python examples/03_granite_open_model.py
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
        attest_granite_open_weights=True,
        regulatory_context={
            "article_50_paragraph": "1",
            "deployer_jurisdiction": "DE",
            "end_user_disclosure_made": True,
            "notes": "Granite 3.x open weights; reproducible from Hugging Face.",
        },
    )

    response = model.chat(
        messages=[{"role": "user", "content": "Summarise GDPR in one sentence."}],
    )
    print("Assistant:", response["choices"][0]["message"]["content"])
    print(
        "\nReceipt emitted with schema=granite_open_model/v1, "
        "license=Apache-2.0, reproducible=true."
    )


if __name__ == "__main__":
    main()
