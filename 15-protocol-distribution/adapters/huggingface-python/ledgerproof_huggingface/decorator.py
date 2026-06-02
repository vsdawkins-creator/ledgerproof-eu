"""@lpr_track decorator — wrap any function that returns an HF response.

```python
from huggingface_hub import InferenceClient
from ledgerproof_huggingface import lpr_track

client = InferenceClient(model="meta-llama/Llama-3.1-70B-Instruct")

@lpr_track(deployer_id="urn:eu:deployer:acme")
def ask(question: str):
    return client.chat_completion(
        messages=[{"role": "user", "content": question}],
    )
```

Async functions are auto-detected. The decorator inspects `kwargs` for
`messages=` (or `prompt=`) so the prompt hash is bound; pass them through
as keywords for best results.
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
    prompt_kwarg: str = "prompt",
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator factory."""
    signer = signer or Ed25519Signer()
    emitter = emitter or LogEmitter()

    def _extract(args: tuple, kwargs: dict) -> tuple[list[dict] | None, str | None]:
        messages = kwargs.get(messages_kwarg)
        prompt = kwargs.get(prompt_kwarg)
        return messages, prompt

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        if asyncio.iscoroutinefunction(fn) or inspect.iscoroutinefunction(fn):

            @functools.wraps(fn)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                resp = await fn(*args, **kwargs)
                try:
                    messages, prompt = _extract(args, kwargs)
                    emit_receipt(
                        resp,
                        deployer_id=deployer_id,
                        messages=messages,
                        prompt=prompt,
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
                messages, prompt = _extract(args, kwargs)
                emit_receipt(
                    resp,
                    deployer_id=deployer_id,
                    messages=messages,
                    prompt=prompt,
                    regulatory_context=regulatory_context,
                    signer=signer,
                    emitter=emitter,
                )
            except Exception:  # noqa: BLE001
                pass
            return resp

        return sync_wrapper

    return decorator
