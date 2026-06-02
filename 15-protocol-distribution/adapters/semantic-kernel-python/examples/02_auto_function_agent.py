"""Example 2: auto-function-calling agent with LedgerProofAutoFunctionFilter.

Demonstrates how to attach the auto-function filter so that every tool the
LLM-driven agent calls produces an `agent_function_invocation/v1` receipt
with `is_auto_invoked=True`.

Requires: pip install "ledgerproof-semantic-kernel[sk]" and a configured
OpenAI / Azure OpenAI key.
"""

import asyncio
import os

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.function_choice_behavior import (
    FunctionChoiceBehavior,
)
from semantic_kernel.connectors.ai.open_ai import (
    OpenAIChatCompletion,
    OpenAIChatPromptExecutionSettings,
)
from semantic_kernel.contents import ChatHistory
from semantic_kernel.functions import kernel_function

from ledgerproof_semantic_kernel import (
    Ed25519Signer,
    LedgerProofAutoFunctionFilter,
    LogEmitter,
)


class CalculatorPlugin:
    @kernel_function(description="Add two integers.")
    def add(self, a: int, b: int) -> int:
        return a + b


async def main() -> None:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Set OPENAI_API_KEY to run this example.")
        return

    kernel = Kernel()
    kernel.add_service(
        OpenAIChatCompletion(ai_model_id="gpt-4o-mini", api_key=api_key)
    )
    kernel.add_plugin(CalculatorPlugin(), plugin_name="calc")

    kernel.add_filter(
        "auto_function_invocation",
        LedgerProofAutoFunctionFilter(
            deployer_id="acme-agent-001",
            emitter=LogEmitter("./receipts.jsonl"),
            signer=Ed25519Signer(),
        ),
    )

    history = ChatHistory()
    history.add_user_message("What is 17 + 25? Use the calculator.")

    settings = OpenAIChatPromptExecutionSettings(
        function_choice_behavior=FunctionChoiceBehavior.Auto(),
    )
    chat = kernel.get_service(type=OpenAIChatCompletion)
    reply = await chat.get_chat_message_content(
        chat_history=history, settings=settings, kernel=kernel
    )
    print("Agent reply:", reply)


if __name__ == "__main__":
    asyncio.run(main())
