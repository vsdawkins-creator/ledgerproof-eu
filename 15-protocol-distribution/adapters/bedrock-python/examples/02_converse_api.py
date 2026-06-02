"""
Bedrock Converse API example using `make_client` factory.

The Converse API is provider-agnostic — try swapping the modelId between
Anthropic / Meta / Mistral / Amazon Titan without changing the call shape.
The receipt records the upstream provider attribution automatically.

    python examples/02_converse_api.py
"""

from __future__ import annotations

import logging
import sys

from ledgerproof_bedrock import StderrEmitter, make_client


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    try:
        import boto3  # noqa: F401
    except ImportError:
        print("boto3 not installed. Run `pip install -e .` in the adapter dir.")
        sys.exit(1)

    # `make_client` wires up both legacy invoke_model and Converse methods.
    client = make_client(
        deployer_id="acme-eu-bank",
        region_name="eu-central-1",
        emitter=StderrEmitter(),
        regulatory_context={
            "article_50_paragraph": "1",
            "deployer_jurisdiction": "DE",
            "end_user_disclosure_made": True,
        },
    )

    for model_id in (
        "anthropic.claude-3-haiku-20240307-v1:0",
        "mistral.mistral-large-2402-v1:0",
        "amazon.titan-text-express-v1",
    ):
        try:
            response = client.converse(
                modelId=model_id,
                messages=[
                    {"role": "user", "content": [{"text": "Reply with one word."}]}
                ],
                inferenceConfig={"maxTokens": 20},
            )
            text = response["output"]["message"]["content"][0].get("text", "")
            print(f"[{model_id}] -> {text!r}")
        except Exception as exc:  # noqa: BLE001
            # Model may not be enabled in this region for your account.
            print(f"[{model_id}] skipped: {exc}")


if __name__ == "__main__":
    main()
