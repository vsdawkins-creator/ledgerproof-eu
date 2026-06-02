"""
Quickstart: drop-in wrapper for boto3 bedrock-runtime.

Run after `pip install -e .` from the adapter directory:
    AWS_PROFILE=... python examples/01_bedrock_quickstart.py

The receipt is printed as a JSON line to the logger configured by LogEmitter
(by default the `ledgerproof.receipt` logger). The Bedrock response body is
returned unchanged — constraint C7.
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
        regulatory_context={
            "article_50_paragraph": "1",
            "deployer_jurisdiction": "DE",
            "end_user_disclosure_made": True,
            "notes": "Customer-facing chatbot; disclosure shown pre-conversation.",
        },
    )

    response = client.invoke_model(
        modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
        body=json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [{"role": "user", "content": "Say hello in German."}],
                "max_tokens": 50,
            }
        ),
    )

    body = json.loads(response["body"].read())
    print("\nAssistant text:")
    print(body["content"][0]["text"])


if __name__ == "__main__":
    main()
