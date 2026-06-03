"""
Function calling example: FireFunction-v2 on Fireworks with tool-use refs in the receipt.

FireFunction is Fireworks's open-weights function-calling model. Tool calls in
the response are hashed (input arguments only — never raw arguments) and
recorded in the receipt's `tool_uses` array, alongside the chatbot session
content refs.
"""

from __future__ import annotations

import json
import os

from ledgerproof_fireworks import (
    LedgerProofFireworks,
    OpenModelAttribution,
    RegulatoryContext,
    StderrEmitter,
)


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"},
                    "unit": {"type": "string", "enum": ["c", "f"]},
                },
                "required": ["city"],
            },
        },
    }
]


def main() -> None:
    client = LedgerProofFireworks(
        deployer_id="acme-agent-eu",
        api_key=os.environ.get("FIREWORKS_API_KEY"),
        emitter=StderrEmitter(),
        schema="open_model_hosted/v1",
        regulatory_context=RegulatoryContext(
            article_50_paragraph="1",
            deployer_jurisdiction="FR",
            end_user_disclosure_made=True,
            notes="Agentic assistant with weather + calendar tools.",
        ),
        open_model=OpenModelAttribution(
            underlying_model_family="firefunction",
            underlying_model_provider="fireworks",
            host_provider="fireworks",
            model_license="apache-2.0",
        ),
    )

    response = client.chat.completions.create(
        model="accounts/fireworks/models/firefunction-v2",
        messages=[
            {"role": "user", "content": "What's the weather in Berlin in Celsius?"},
        ],
        tools=TOOLS,
        tool_choice="auto",
    )

    msg = response.choices[0].message
    print("---- Assistant tool call ----")
    if getattr(msg, "tool_calls", None):
        for tc in msg.tool_calls:
            print(f"  {tc.function.name}({tc.function.arguments})")
    else:
        print(msg.content)
    print("---- (A receipt with tool_uses[] hashes was emitted on stderr) ----")


if __name__ == "__main__":
    main()
