"""Anthropic SDK adapter — same monkey-patch pattern as openai.py.

Wraps ``client.messages.create`` (sync + async + streaming). The Anthropic
response shape differs from OpenAI's; this module owns the extraction.

Usage::

    import anthropic
    import ledgerproof

    client = anthropic.Anthropic()
    ledgerproof.attach(
        client,
        publisher_id="LEI:5493001KJTIIGC8Y1R12",
        deployer_country="DE",
        deployer_name="Acme Corp",
    )

    message = client.messages.create(
        model="claude-sonnet-4-6-20251022",
        max_tokens=1024,
        messages=[{"role": "user", "content": "Hello"}],
    )
    # message._ledgerproof_future is a concurrent.futures.Future
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

logger = logging.getLogger("ledgerproof.adapters.anthropic")

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
    """Patch the Anthropic client to auto-issue LPR receipts. Idempotent."""
    clients = _resolve_clients(target)
    if not clients:
        raise LedgerProofError(
            f"Could not locate an Anthropic client on {target!r}. "
            f"Pass an explicit anthropic.Anthropic() or anthropic.AsyncAnthropic()."
        )

    lp = LedgerProof(
        publisher_id=publisher_id,
        deployer_country=deployer_country,
        api_key=api_key,
        api_base=api_base,
    )
    executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="ledgerproof-anthropic")

    settings = {
        "lp": lp,
        "executor": executor,
        "deployer_name": deployer_name,
        "ai_system_id_override": ai_system_id,
        "is_public_interest": is_public_interest,
    }

    for client in clients:
        key = id(client)
        if key in _PATCHED:
            continue
        messages_ns = getattr(client, "messages", None)
        if messages_ns is None:
            continue
        is_async = type(client).__name__.startswith("Async")
        original_create = messages_ns.create
        wrapped = (
            _wrap_async_create(original_create, settings)
            if is_async
            else _wrap_sync_create(original_create, settings)
        )
        messages_ns.create = wrapped
        _PATCHED[key] = {
            "messages": messages_ns,
            "original_create": original_create,
            "settings": settings,
        }
        logger.info(
            "Attached LedgerProof to %s Anthropic client.",
            "async" if is_async else "sync",
        )


def detach(target: Any) -> None:
    """Reverse :func:`attach`. Idempotent."""
    for client in _resolve_clients(target):
        info = _PATCHED.pop(id(client), None)
        if info is None:
            continue
        info["messages"].create = info["original_create"]
        info["settings"]["executor"].shutdown(wait=False)


def _wrap_sync_create(original: Callable[..., Any], settings: dict[str, Any]) -> Callable[..., Any]:
    @functools.wraps(original)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        is_stream = bool(kwargs.get("stream", False))
        response = original(*args, **kwargs)
        if is_stream:
            return _wrap_stream(response, settings, kwargs)
        text = _extract_text(response)
        if text:
            _schedule_receipt(text, settings, response, kwargs)
        return response

    return wrapped


def _wrap_async_create(original: Callable[..., Any], settings: dict[str, Any]) -> Callable[..., Any]:
    @functools.wraps(original)
    async def wrapped(*args: Any, **kwargs: Any) -> Any:
        is_stream = bool(kwargs.get("stream", False))
        response = await original(*args, **kwargs)
        if is_stream:
            return _wrap_async_stream(response, settings, kwargs)
        text = _extract_text(response)
        if text:
            _schedule_receipt(text, settings, response, kwargs)
        return response

    return wrapped


def _wrap_stream(stream: Any, settings: dict[str, Any], kwargs: dict[str, Any]) -> Any:
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
                    _schedule_receipt(full, settings, stream, kwargs)
                raise
            text = _extract_text_from_chunk(chunk)
            if text:
                chunks.append(text)
            return chunk

        def __getattr__(self, name: str) -> Any:
            return getattr(stream, name)

    return _StreamWrapper()


def _wrap_async_stream(stream: Any, settings: dict[str, Any], kwargs: dict[str, Any]) -> Any:
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
                    _schedule_receipt(full, settings, stream, kwargs)
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
    future: Future[Receipt | None] = executor.submit(
        _issue_safe, text, settings, call_kwargs
    )
    try:
        response._ledgerproof_future = future  # type: ignore[attr-defined]
    except (AttributeError, TypeError):
        pass


def _issue_safe(text: str, settings: dict[str, Any], call_kwargs: dict[str, Any]) -> Any:
    try:
        lp: LedgerProof = settings["lp"]
        model = call_kwargs.get("model", "anthropic/unknown")
        ai_system_id = settings["ai_system_id_override"] or f"anthropic/{model}"
        receipt = lp.publish_ai_article_50(
            artifact=text,
            artifact_content_type="text/plain",
            ai_system_id=ai_system_id,
            deployer_name=settings["deployer_name"],
            content_category="SYNTHETIC_TEXT",
            generation_type="FULLY_GENERATED",
            is_public_interest=settings["is_public_interest"],
        )
        logger.debug("Issued seq=%d hash=%s", receipt.sequence, receipt.entry_hash[:16])
        return receipt
    except LedgerProofError as exc:
        logger.warning("Receipt issuance failed (fail-open): %s", exc)
        return None


def _extract_text(message: Any) -> str:
    """Anthropic responses have ``content`` as a list of blocks: text + tool_use."""
    try:
        content = message.content
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts: list[str] = []
            for block in content:
                if isinstance(block, dict):
                    if block.get("type") == "text":
                        parts.append(block.get("text", ""))
                else:
                    block_type = getattr(block, "type", None)
                    if block_type == "text":
                        parts.append(getattr(block, "text", ""))
            return "".join(parts)
        return ""
    except (AttributeError, TypeError):
        return ""


def _extract_text_from_chunk(event: Any) -> str:
    """Anthropic streaming events: content_block_delta with text_delta."""
    try:
        event_type = getattr(event, "type", None) or (event.get("type") if isinstance(event, dict) else None)
        if event_type != "content_block_delta":
            return ""
        delta = getattr(event, "delta", None) or (event.get("delta") if isinstance(event, dict) else None)
        if delta is None:
            return ""
        delta_type = getattr(delta, "type", None) or (delta.get("type") if isinstance(delta, dict) else None)
        if delta_type != "text_delta":
            return ""
        text = getattr(delta, "text", None) or (delta.get("text") if isinstance(delta, dict) else None)
        return text or ""
    except (AttributeError, TypeError):
        return ""


def _resolve_clients(target: Any) -> list[Any]:
    if hasattr(target, "messages"):
        return [target]
    return []


__all__ = ["attach", "detach"]
