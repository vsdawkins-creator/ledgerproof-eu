"""Mistral AI SDK adapter (mistralai package).

Wraps ``client.chat.complete`` (sync) and ``client.chat.complete_async`` (async).
Response shape mirrors OpenAI's: ``response.choices[0].message.content``.
"""

from __future__ import annotations

import functools
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, Any, Callable

from ..client import LedgerProof
from ..errors import LedgerProofError

if TYPE_CHECKING:
    from concurrent.futures import Future

    from ..types import Receipt

logger = logging.getLogger("ledgerproof.adapters.mistral")

_PATCHED: dict[int, dict[str, Any]] = {}


def attach(
    target: Any,
    *,
    publisher_id: str,
    deployer_country: str,
    deployer_name: str,
    ai_system_id: str | None = None,
    api_key: str | None = None,
    api_base: str | None = None,
    is_public_interest: bool | None = None,
) -> None:
    chat = getattr(target, "chat", None)
    if chat is None:
        raise LedgerProofError(
            f"Could not locate a Mistral client.chat namespace on {target!r}."
        )
    key = id(target)
    if key in _PATCHED:
        return

    lp = LedgerProof(
        publisher_id=publisher_id,
        deployer_country=deployer_country,
        api_key=api_key,
        api_base=api_base,
    )
    executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="ledgerproof-mistral")
    settings = {
        "lp": lp,
        "executor": executor,
        "deployer_name": deployer_name,
        "ai_system_id_override": ai_system_id,
        "is_public_interest": is_public_interest,
    }

    patched: dict[str, Callable[..., Any]] = {}
    for method_name in ("complete", "complete_async", "stream", "stream_async"):
        if not hasattr(chat, method_name):
            continue
        original = getattr(chat, method_name)
        is_async = "async" in method_name
        is_stream = "stream" in method_name
        wrapped = _wrap(original, settings, is_async=is_async, is_stream=is_stream)
        setattr(chat, method_name, wrapped)
        patched[method_name] = original

    _PATCHED[key] = {"target": target, "chat": chat, "originals": patched, "settings": settings}
    logger.info("Attached LedgerProof to Mistral client.")


def detach(target: Any) -> None:
    info = _PATCHED.pop(id(target), None)
    if info is None:
        return
    for name, original in info["originals"].items():
        setattr(info["chat"], name, original)
    info["settings"]["executor"].shutdown(wait=False)


def _wrap(
    original: Callable[..., Any],
    settings: dict[str, Any],
    *,
    is_async: bool,
    is_stream: bool,
) -> Callable[..., Any]:
    if is_async:

        @functools.wraps(original)
        async def async_wrapped(*args: Any, **kwargs: Any) -> Any:
            result = await original(*args, **kwargs)
            if is_stream:
                return _wrap_async_stream(result, settings, kwargs)
            text = _extract_text(result)
            if text:
                _schedule_receipt(text, settings, result, kwargs)
            return result

        return async_wrapped

    @functools.wraps(original)
    def sync_wrapped(*args: Any, **kwargs: Any) -> Any:
        result = original(*args, **kwargs)
        if is_stream:
            return _wrap_stream(result, settings, kwargs)
        text = _extract_text(result)
        if text:
            _schedule_receipt(text, settings, result, kwargs)
        return result

    return sync_wrapped


def _wrap_stream(stream: Any, settings: dict[str, Any], call_kwargs: dict[str, Any]) -> Any:
    chunks: list[str] = []

    class _StreamWrapper:
        def __iter__(self) -> Any:
            return self

        def __next__(self) -> Any:
            try:
                chunk = next(stream)
            except StopIteration:
                full = "".join(chunks)
                if full:
                    _schedule_receipt(full, settings, stream, call_kwargs)
                raise
            text = _extract_text_from_chunk(chunk)
            if text:
                chunks.append(text)
            return chunk

        def __getattr__(self, name: str) -> Any:
            return getattr(stream, name)

    return _StreamWrapper()


def _wrap_async_stream(stream: Any, settings: dict[str, Any], call_kwargs: dict[str, Any]) -> Any:
    chunks: list[str] = []

    class _AsyncStreamWrapper:
        def __aiter__(self) -> Any:
            return self

        async def __anext__(self) -> Any:
            try:
                chunk = await stream.__anext__()
            except StopAsyncIteration:
                full = "".join(chunks)
                if full:
                    _schedule_receipt(full, settings, stream, call_kwargs)
                raise
            text = _extract_text_from_chunk(chunk)
            if text:
                chunks.append(text)
            return chunk

        def __getattr__(self, name: str) -> Any:
            return getattr(stream, name)

    return _AsyncStreamWrapper()


def _schedule_receipt(
    text: str, settings: dict[str, Any], response: Any, call_kwargs: dict[str, Any]
) -> None:
    executor: ThreadPoolExecutor = settings["executor"]
    future: Future[Receipt | None] = executor.submit(_issue_safe, text, settings, call_kwargs)
    try:
        response._ledgerproof_future = future  # type: ignore[attr-defined]
    except (AttributeError, TypeError):
        pass


def _issue_safe(text: str, settings: dict[str, Any], call_kwargs: dict[str, Any]) -> Any:
    try:
        lp: LedgerProof = settings["lp"]
        model = call_kwargs.get("model", "mistral/unknown")
        ai_system_id = settings["ai_system_id_override"] or f"mistral/{model}"
        return lp.publish_ai_article_50(
            artifact=text,
            artifact_content_type="text/plain",
            ai_system_id=ai_system_id,
            deployer_name=settings["deployer_name"],
            content_category="SYNTHETIC_TEXT",
            generation_type="FULLY_GENERATED",
            is_public_interest=settings["is_public_interest"],
        )
    except LedgerProofError as exc:
        logger.warning("Receipt issuance failed (fail-open): %s", exc)
        return None


def _extract_text(response: Any) -> str:
    try:
        choices = response.choices
        if not choices:
            return ""
        message = choices[0].message
        content = getattr(message, "content", None)
        return content if isinstance(content, str) else ""
    except (AttributeError, IndexError, TypeError):
        return ""


def _extract_text_from_chunk(chunk: Any) -> str:
    try:
        data = getattr(chunk, "data", chunk)
        choices = data.choices
        if not choices:
            return ""
        delta = choices[0].delta
        content = getattr(delta, "content", None)
        return content if isinstance(content, str) else ""
    except (AttributeError, IndexError, TypeError):
        return ""


__all__ = ["attach", "detach"]
