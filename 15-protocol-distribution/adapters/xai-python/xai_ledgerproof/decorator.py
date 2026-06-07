"""@lpr_track decorator — wrap any function that returns an xAI Grok ChatCompletion.

```python
import os
from openai import OpenAI
from xai_ledgerproof import lpr_track

client = OpenAI(
    api_key=os.environ["XAI_API_KEY"],
    base_url="https://api.x.ai/v1",
)

@lpr_track(deployer_id="urn:eu:deployer:acme")
def ask(question: str, *, messages):
    return client.chat.completions.create(
        model="grok-2-latest",
        messages=messages,
    )
```

Async functions are auto-detected. The decorator inspects `kwargs` for
`messages=` so the prompt hash is bound; if the wrapped function passes
messages positionally, you can hint via `messages_kwarg="..."` or pass
them through a `messages=` keyword to your own function.
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
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator factory."""
    signer = signer or Ed25519Signer()
    emitter = emitter or LogEmitter()

    def _extract_messages(args: tuple, kwargs: dict) -> list[dict[str, Any]] | None:
        if messages_kwarg in kwargs:
            return kwargs[messages_kwarg]
        return None

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        if asyncio.iscoroutinefunction(fn) or inspect.iscoroutinefunction(fn):

            @functools.wraps(fn)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                resp = await fn(*args, **kwargs)
                try:
                    emit_receipt(
                        resp,
                        deployer_id=deployer_id,
                        messages=_extract_messages(args, kwargs),
                        regulatory_context=regulatory_context,
                        signer=signer,
                        emitter=emitter,
                    )
                except Exception:  # noqa: BLE001
                    # C7: receipt failure must never break the caller path
                    pass
                return resp

            return async_wrapper

        @functools.wraps(fn)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            resp = fn(*args, **kwargs)
            try:
                emit_receipt(
                    resp,
                    deployer_id=deployer_id,
                    messages=_extract_messages(args, kwargs),
                    regulatory_context=regulatory_context,
                    signer=signer,
                    emitter=emitter,
                )
            except Exception:  # noqa: BLE001
                pass
            return resp

        return sync_wrapper

    return decorator
