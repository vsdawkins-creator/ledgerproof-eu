"""@lpr_track decorator for arbitrary Vertex AI / Gemini call sites."""
from __future__ import annotations

from functools import wraps
from typing import Any, Callable

from .emitter import emit_receipt


def lpr_track(
    *,
    schema: str = "generated_content/v1",
    model: str | None = None,
    project: str | None = None,
    location: str | None = None,
    input_arg: str = "prompt",
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorate a function that returns a Vertex AI text-bearing response.

    The decorated function's return value is passed through untouched
    (C7). A receipt is emitted side-channel using the function's `prompt`
    kwarg as input_text and `response.text` as output_text.
    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = fn(*args, **kwargs)
            try:
                input_text = kwargs.get(input_arg)
                if input_text is None and args:
                    input_text = args[0] if isinstance(args[0], str) else None
                output_text = getattr(result, "text", None)
                if not isinstance(output_text, str):
                    output_text = str(result)
                emit_receipt(
                    schema,
                    model=model or "unknown",
                    project=project,
                    location=location,
                    input_text=str(input_text) if input_text is not None else None,
                    output_text=output_text,
                )
            except Exception:
                pass
            return result

        return wrapper

    return decorator
