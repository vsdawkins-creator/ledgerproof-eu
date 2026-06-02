"""@lpr_track decorator — wrap any function returning an Azure OpenAI ChatCompletion.

```python
from openai import AzureOpenAI
from ledgerproof_azure_openai import lpr_track

client = AzureOpenAI(
    azure_endpoint="https://contoso-weu.openai.azure.com/",
    api_key="...",
    api_version="2024-08-01-preview",
)

@lpr_track(
    deployer_id="urn:eu:deployer:contoso-bank",
    azure_endpoint="https://contoso-weu.openai.azure.com/",
    azure_deployment="gpt4-prod",
    api_version="2024-08-01-preview",
    regulatory_context={"schema": "azure_enterprise_session/v1"},
)
def ask(question: str):
    return client.chat.completions.create(
        model="gpt4-prod",
        messages=[{"role": "user", "content": question}],
    )
```

Async functions are auto-detected.
"""

from __future__ import annotations

import asyncio
import functools
import inspect
from typing import Any, Callable

from .emitter import Emitter, LogEmitter
from .manual import emit_receipt
from .signer import Ed25519Signer, Signer


def lpr_track(
    deployer_id: str,
    *,
    regulatory_context: dict[str, Any] | None = None,
    signer: Signer | None = None,
    emitter: Emitter | None = None,
    messages_kwarg: str = "messages",
    azure_endpoint: str | None = None,
    azure_deployment: str | None = None,
    azure_region: str | None = None,
    api_version: str | None = None,
    tenant_id_hash: str | None = None,
    subscription_id_hash: str | None = None,
    azure_ad_principal_hash: str | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator factory."""
    signer = signer or Ed25519Signer()
    emitter = emitter or LogEmitter()

    def _extract_messages(args: tuple, kwargs: dict) -> list[dict[str, Any]] | None:
        if messages_kwarg in kwargs:
            return kwargs[messages_kwarg]
        return None

    def _emit(resp: Any, args: tuple, kwargs: dict) -> None:
        try:
            emit_receipt(
                resp,
                deployer_id=deployer_id,
                messages=_extract_messages(args, kwargs),
                regulatory_context=regulatory_context,
                signer=signer,
                emitter=emitter,
                azure_endpoint=azure_endpoint,
                azure_deployment=azure_deployment,
                azure_region=azure_region,
                api_version=api_version,
                tenant_id_hash=tenant_id_hash,
                subscription_id_hash=subscription_id_hash,
                azure_ad_principal_hash=azure_ad_principal_hash,
            )
        except Exception:  # noqa: BLE001
            # C7: receipt failure must never break the caller path
            pass

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        if asyncio.iscoroutinefunction(fn) or inspect.iscoroutinefunction(fn):

            @functools.wraps(fn)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                resp = await fn(*args, **kwargs)
                _emit(resp, args, kwargs)
                return resp

            return async_wrapper

        @functools.wraps(fn)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            resp = fn(*args, **kwargs)
            _emit(resp, args, kwargs)
            return resp

        return sync_wrapper

    return decorator
