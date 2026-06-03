"""
Quickstart: drop-in wrapper for IBM watsonx.ai ModelInference.

Requires:
    pip install -e .
    export WATSONX_API_KEY=...
    export WATSONX_PROJECT_ID=...

Then:
    python examples/01_watsonx_quickstart.py

The receipt is printed as a JSON line to the logger configured by
LogEmitter (by default the `ledgerproof.receipt` logger). The watsonx.ai
response body is returned unchanged — constraint C7.

LedgerProof is NOT endorsed by IBM.
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
        print("ibm-watsonx-ai not installed. Run `pip install -e .` in the adapter dir.")
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
        regulatory_context={
            "article_50_paragraph": "1",
            "deployer_jurisdiction": "DE",
            "end_user_disclosure_made": True,
            "notes": "Customer-facing chatbot; disclosure shown pre-conversation.",
        },
    )

    response = model.chat(
        messages=[{"role": "user", "content": "Say hello in German."}],
    )

    text = response["choices"][0]["message"]["content"]
    print("\nAssistant text:")
    print(text)


if __name__ == "__main__":
    main()
