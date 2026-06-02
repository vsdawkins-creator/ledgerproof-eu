"""Example 3: Azure OpenAI through SK with enterprise tenant attribution.

Wraps an `AzureChatCompletion` service so that every chat call produces an
`azure_enterprise_session/v1` receipt that pins the call to a specific
Azure Entra ID tenant, subscription scope, and region — the audit
attributes Microsoft enterprise compliance teams need for AI Act 50(1)
inventory.

Stream-aware: the wrapper digests tokens as they arrive; nothing is
buffered.

Requires: pip install "ledgerproof-semantic-kernel[sk]" and Azure OpenAI
credentials. This integration is NOT endorsed by Microsoft.
"""

import asyncio
import os

from semantic_kernel.connectors.ai.open_ai import (
    AzureChatCompletion,
    AzureChatPromptExecutionSettings,
)
from semantic_kernel.contents import ChatHistory

from ledgerproof_semantic_kernel import (
    Ed25519Signer,
    LedgerProofChatService,
    LogEmitter,
)


async def main() -> None:
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
    tenant_id = os.environ.get("AZURE_TENANT_ID", "00000000-0000-0000-0000-000000000000")
    subscription = os.environ.get(
        "AZURE_SUBSCRIPTION_SCOPE",
        "sub/00000000-0000-0000-0000-000000000000",
    )
    region = os.environ.get("AZURE_REGION", "westeurope")

    if not endpoint or not api_key:
        print("Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY to run this example.")
        return

    inner = AzureChatCompletion(
        deployment_name=deployment, endpoint=endpoint, api_key=api_key
    )
    service = LedgerProofChatService(
        inner,
        deployer_id="acme-eu-bank-001",
        schema="azure_enterprise_session/v1",
        emitter=LogEmitter("./receipts.jsonl"),
        signer=Ed25519Signer(),
        extra={
            "tenant_id": tenant_id,
            "subscription_scope": subscription,
            "deployment_region": region,
        },
    )

    history = ChatHistory()
    history.add_user_message(
        "Briefly explain ISO/IEC 42001 to a compliance team."
    )

    settings = AzureChatPromptExecutionSettings()
    print("Assistant: ", end="", flush=True)
    async for chunk in service.get_streaming_chat_message_content(
        chat_history=history, settings=settings
    ):
        # Disclosure: the underlying response is unchanged; the receipt is
        # side-channel-only (C7).
        print(getattr(chunk, "content", ""), end="", flush=True)
    print()


if __name__ == "__main__":
    asyncio.run(main())
