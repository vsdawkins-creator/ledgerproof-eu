"""Example 1: basic Kernel + LedgerProofFunctionFilter.

A weather plugin is added to a Kernel, then invoked. A signed receipt for
the function call is appended to `./receipts.jsonl`.

Requires: pip install "ledgerproof-semantic-kernel[sk]"
"""

import asyncio

from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function

from ledgerproof_semantic_kernel import (
    Ed25519Signer,
    LedgerProofFunctionFilter,
    LogEmitter,
)


class WeatherPlugin:
    @kernel_function(description="Get the weather for a city.")
    def get_weather(self, city: str) -> str:
        return f"Sunny in {city}"


async def main() -> None:
    kernel = Kernel()
    kernel.add_plugin(WeatherPlugin(), plugin_name="weather")
    kernel.add_filter(
        "function_invocation",
        LedgerProofFunctionFilter(
            deployer_id="acme-deployer-001",
            emitter=LogEmitter("./receipts.jsonl"),
            signer=Ed25519Signer(),
        ),
    )
    result = await kernel.invoke(
        function_name="get_weather", plugin_name="weather", city="Paris"
    )
    print("Function result:", result)
    print("Receipt written to ./receipts.jsonl")


if __name__ == "__main__":
    asyncio.run(main())
