"""``@lpr_track`` decorator.

Wraps any callable so that, on return, a LedgerProof receipt is emitted
describing the prompt fed in and the completion returned. Works for both
sync and async callables.

The decorator does not modify the wrapped function's return value (C7).
"""

from __future__ import annotations

import functools
import inspect
from typing import Any, Awaitable, Callable, Mapping, Optional

from .emitter import Emitter
from .manual import emit_receipt
from .signer import EphemeralEd25519Signer


def _resolve_prompt(args: tuple[Any, ...], kwargs: Mapping[str, Any], prompt_arg: str) -> str:
    if prompt_arg in kwargs:
        return str(kwargs[prompt_arg])
    if args:
        return str(args[0])
    return ""


def _resolve_completion(result: Any) -> str:
    if isinstance(result, str):
        return result
    # If the wrapped function returns an aleph-alpha CompletionResponse we
    # try to extract `.completions[0].completion`. Otherwise fall back to repr.
    completions = getattr(result, "completions", None)
    if completions:
        return getattr(completions[0], "completion", "") or ""
    return repr(result)


def lpr_track(
    *,
    article: str = "50(2)",
    schema: str = "generated_content/v1",
    model: str = "unknown",
    prompt_arg: str = "prompt",
    extra: Optional[Mapping[str, Any]] = None,
    emitter: Optional[Emitter] = None,
    signer: Optional[EphemeralEd25519Signer] = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorate a function so its prompt/completion are recorded.

    Example::

        @lpr_track(article="50(1)", schema="chatbot_session/v1", model="luminous-base")
        def chat(prompt: str) -> str:
            ...
    """

    def decorate(fn: Callable[..., Any]) -> Callable[..., Any]:
        if inspect.iscoroutinefunction(fn):

            @functools.wraps(fn)
            async def awrapper(*args: Any, **kwargs: Any) -> Any:
                result = await fn(*args, **kwargs)
                emit_receipt(
                    article=article,
                    schema=schema,
                    prompt_text=_resolve_prompt(args, kwargs, prompt_arg),
                    completion_text=_resolve_completion(result),
                    model=model,
                    extra=extra,
                    emitter=emitter,
                    signer=signer,
                )
                return result

            return awrapper

        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = fn(*args, **kwargs)
            emit_receipt(
                article=article,
                schema=schema,
                prompt_text=_resolve_prompt(args, kwargs, prompt_arg),
                completion_text=_resolve_completion(result),
                model=model,
                extra=extra,
                emitter=emitter,
                signer=signer,
            )
            return result

        return wrapper

    return decorate
