"""Local Transformers pipeline — self-hosted inference with on-prem receipt.

For deployers running models inside their own perimeter (on-prem, air-gapped,
or sovereign-cloud). The `local_inference/v1` schema records the host
environment so the receipt demonstrates the inference did not leave the
deployer's controlled infrastructure.

Requires the `transformers` optional dependency:
    pip install "ledgerproof-huggingface[transformers]" torch

This example uses a small open model for tractability; swap for Llama-3.1-8B
or a model of your choice in production.
"""

from __future__ import annotations

from ledgerproof_huggingface import LedgerProofPipeline


def main() -> None:
    # Import locally so the example file imports even if `transformers`
    # isn't installed.
    from transformers import pipeline  # type: ignore

    pipe = pipeline(
        "text-generation",
        model="gpt2",  # swap for "meta-llama/Llama-3.1-8B-Instruct" in production
    )

    lp_pipe = LedgerProofPipeline(
        pipe,
        deployer_id="urn:eu:deployer:acme-bank-de",
        regulatory_context={
            "schema": "local_inference/v1",
            "jurisdiction": "EU",
            # host_environment is auto-populated; override here if you want
            # to inject e.g. a DC region, GPU SKU, or rack ID.
        },
    )

    result = lp_pipe("The quick brown fox", max_new_tokens=20)

    print("\n--- Model output ---")
    print(result[0]["generated_text"])
    print("--- (signed local_inference/v1 receipt was emitted above) ---\n")


if __name__ == "__main__":
    main()
