"""
Claude Agent SDK-style example. When the response contains tool_use blocks the
adapter promotes the schema to `agent_action/v1` and binds hashed tool inputs
into the receipt.
"""

from __future__ import annotations

from ledgerproof_anthropic import LedgerProofAnthropic, StderrEmitter


def main() -> None:
    client = LedgerProofAnthropic(
        deployer_id="acme-corp-eu",
        emitter=StderrEmitter(),
    )

    tools = [
        {
            "name": "get_weather",
            "description": "Get the current weather for a city.",
            "input_schema": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        }
    ]

    response = client.messages.create(
        model="claude-opus-4-1",
        max_tokens=512,
        tools=tools,
        messages=[{"role": "user", "content": "What's the weather in Berlin?"}],
    )

    print("---- Stop reason:", response.stop_reason, "----")
    for block in response.content:
        btype = getattr(block, "type", None)
        if btype == "text":
            print("text:", block.text)
        elif btype == "tool_use":
            print(f"tool_use: name={block.name} id={block.id} input={block.input}")

    print("---- (An agent_action/v1 receipt was emitted on stderr) ----")


if __name__ == "__main__":
    main()
