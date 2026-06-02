"""
EU region deployment with explicit data-residency attestation.

The receipt switches to the `eu_aws_data_residency/v1` schema and records:
  - the attested region (e.g. eu-west-1)
  - whether SCCs are in place
  - the region pulled from the boto3 client config (cross-checked at verify time)

This is useful for deployers under GDPR + EU AI Act who must demonstrate that
inference for EU end-users does NOT cross the region boundary.

    python examples/03_eu_region_residency.py
"""

from __future__ import annotations

import json
import logging
import sys

from ledgerproof_bedrock import LedgerProofBedrockClient, StderrEmitter


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    try:
        import boto3
    except ImportError:
        print("boto3 not installed. Run `pip install -e .` in the adapter dir.")
        sys.exit(1)

    raw = boto3.client("bedrock-runtime", region_name="eu-west-1")

    client = LedgerProofBedrockClient(
        deployer_id="acme-eu-bank",
        client=raw,
        emitter=StderrEmitter(),
        attest_residency=True,
        sccs_in_place=True,
        regulatory_context={
            "article_50_paragraph": "1",
            "deployer_jurisdiction": "IE",
            "end_user_disclosure_made": True,
            "notes": "EU end-user; inference confined to eu-west-1.",
        },
    )

    response = client.invoke_model(
        modelId="anthropic.claude-3-haiku-20240307-v1:0",
        body=json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [{"role": "user", "content": "Bonjour"}],
                "max_tokens": 20,
            }
        ),
    )

    body = json.loads(response["body"].read())
    print("Assistant:", body["content"][0]["text"])
    print(
        "\nReceipt was emitted with schema=eu_aws_data_residency/v1, "
        "attested_region=eu-west-1, eu_region=true, sccs_in_place=true."
    )


if __name__ == "__main__":
    main()
