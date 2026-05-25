"""OpenAI SDK adapter — the headline ``attach()`` feature.

Wraps ``client.chat.completions.create`` (sync + async) so that every
completion automatically issues an LPR Article 50 receipt. The user's call
returns immediately; the receipt is issued in the background.

Usage::

    import openai
    import ledgerproof

    client = openai.OpenAI()
    ledgerproof.attach(
        client,
        publisher_id="LEI:5493001KJTIIGC8Y1R12",
        deployer_country="DE",
        deployer_name="Acme Corp",
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Write a haiku about Bitcoin."}],
    )
    # response works exactly as before. response._ledgerproof_future is a
    # concurrent.futures.Future you can await if you want the receipt synchronously.

Design choices:

- The patch targets the client's ``chat.completions.create`` method. Other
  endpoints (``responses.create``, ``images.generate``, ``audio.speech.create``)
  are out of scope for this release; they each have different output shapes
  and need bespoke extraction. Coming in Sprint 2.
- Receipt issuance runs in a ThreadPoolExecutor — non-blocking, fails open.
- Streaming completions are handled by wrapping the iterator and emitting
  a single receipt at stream-end (the accumulated text).
- ``detach()`` restores the original method exactly.
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

logger = logging.getLogger("ledgerproof.adapters.openai")

# Each patched client gets a registry entry tracking what we patched and how
# to undo it. Keyed by ``id(client)``.
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
    """Patch the OpenAI client to auto-issue LPR receipts on every chat completion.

    Idempotent: calling twice on the same client is a no-op.

    :param target: Either the ``openai`` module (we'll use its module-level
        client) or an explicit ``openai.OpenAI`` / ``openai.AsyncOpenAI`` instance.
    :param publisher_id: Your legal-entity identifier (LEI/EUID/VAT/DID).
    :param deployer_country: ISO 3166-1 alpha-2 country code.
    :param deployer_name: Human-readable organization name.
    :param ai_system_id: Override the AI system identifier in the receipt.
        Default is derived from the ``model`` parameter on each call.
    :param api_key: LedgerProof API key. Falls back to ``LEDGERPROOF_API_KEY``.
    :param api_base: LedgerProof endpoint. Defaults to api-eu.ledgerproofhq.io.
    :param is_public_interest: Tag every receipt with this assertion.
    """
    clients = _resolve_clients(target)
    if not clients:
        raise LedgerProofError(
            f"Could not locate an OpenAI client on {target!r}. "
            f"Pass an explicit openai.OpenAI() or openai.AsyncOpenAI() instance."
        )

    # Construct the LedgerProof client once per attach.
    lp = LedgerProof(
        publisher_id=publisher_id,
        deployer_country=deployer_country,
        api_key=api_key,
        api_base=api_base,
    )
    executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="ledgerproof-openai")

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
            logger.debug("client %r already attached; no-op", client)
            continue

        # Walk down to the chat.completions namespace.
        completions = _get_completions_namespace(client)
        if completions is None:
            logger.warning(
                "client %r has no chat.completions namespace; skipping", client
            )
            continue

        is_async = _is_async_client(client)
        original_create = completions.create

        if is_async:
            wrapped = _wrap_async_create(original_create, settings)
        else:
            wrapped = _wrap_sync_create(original_create, settings)

        completions.create = wrapped
        _PATCHED[key] = {
            "client": client,
            "completions": completions,
            "original_create": original_create,
            "is_async": is_async,
            "settings": settings,
        }
        logger.info(
            "Attached LedgerProof to %s OpenAI client. Every completion will issue a receipt.",
            "async" if is_async else "sync",
        )


def detach(target: Any) -> None:
    """Reverse :func:`attach` on the given target. Idempotent."""
    clients = _resolve_clients(target)
    for client in clients:
        key = id(client)
        info = _PATCHED.pop(key, None)
        if info is None:
            continue
        info["completions"].create = info["original_create"]
        executor = info["settings"]["executor"]
        executor.shutdown(wait=False)
        logger.info("Detached LedgerProof from OpenAI client %r", client)


# ── Wrappers ────────────────────────────────────────────────────────────────


def _wrap_sync_create(original: Callable[..., Any], settings: dict[str, Any]) -> Callable[..., Any]:
    """Wrap the sync ``chat.completions.create`` method."""

    @functools.wraps(original)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        # If streaming, we need to consume to extract text. Defer to a
        # streaming-aware path.
        is_stream = bool(kwargs.get("stream", False))
        response = original(*args, **kwargs)
        if is_stream:
            return _wrap_stream(response, settings, kwargs)
        text = _extract_text_from_response(response)
        if text:
            _schedule_receipt(text, settings, response, kwargs)
        return response

    return wrapped


def _wrap_async_create(original: Callable[..., Any], settings: dict[str, Any]) -> Callable[..., Any]:
    """Wrap the async ``chat.completions.create`` coroutine."""

    @functools.wraps(original)
    async def wrapped(*args: Any, **kwargs: Any) -> Any:
        is_stream = bool(kwargs.get("stream", False))
        response = await original(*args, **kwargs)
        if is_stream:
            return _wrap_async_stream(response, settings, kwargs)
        text = _extract_text_from_response(response)
        if text:
            _schedule_receipt(text, settings, response, kwargs)
        return response

    return wrapped


def _wrap_stream(stream: Any, settings: dict[str, Any], kwargs: dict[str, Any]) -> Any:
    """Wrap a sync streaming response. Issues one receipt at stream-end."""
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
    """Wrap an async streaming response."""
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


# ── Receipt issuance ───────────────────────────────────────────────────────


def _schedule_receipt(
    text: str,
    settings: dict[str, Any],
    response: Any,
    call_kwargs: dict[str, Any],
) -> None:
    """Submit the receipt-issuance job to the background executor."""
    executor: ThreadPoolExecutor = settings["executor"]
    future: Future[Receipt] = executor.submit(
        _issue_receipt_safe, text, settings, call_kwargs
    )
    # Attach the future to the response object so the caller can await it
    # if they want — e.g., for serializing the receipt_id into a downstream
    # database record.
    try:
        response._ledgerproof_future = future  # type: ignore[attr-defined]
    except (AttributeError, TypeError):
        # Some response types are frozen / pydantic strict — skip silently.
        pass


def _issue_receipt_safe(
    text: str, settings: dict[str, Any], call_kwargs: dict[str, Any]
) -> Any:
    """Issue the receipt, swallowing all errors (fail open).

    Returns the Receipt on success, None on failure. Logged but never raised
    from the background thread.
    """
    try:
        lp: LedgerProof = settings["lp"]
        model = call_kwargs.get("model", "openai/unknown")
        ai_system_id = settings["ai_system_id_override"] or f"openai/{model}"
        receipt = lp.publish_ai_article_50(
            artifact=text,
            artifact_content_type="text/plain",
            ai_system_id=ai_system_id,
            deployer_name=settings["deployer_name"],
            content_category="SYNTHETIC_TEXT",
            generation_type="FULLY_GENERATED",
            is_public_interest=settings["is_public_interest"],
        )
        logger.debug("Issued LPR receipt seq=%d hash=%s", receipt.sequence, receipt.entry_hash[:16])
        return receipt
    except LedgerProofError as exc:
        logger.warning("LedgerProof receipt issuance failed (fail-open): %s", exc)
        return None
    except Exception as exc:  # pragma: no cover
        logger.warning("LedgerProof receipt issuance hit unexpected error (fail-open): %s", exc)
        return None


# ── Text extraction ────────────────────────────────────────────────────────


def _extract_text_from_response(response: Any) -> str:
    """Pull the assistant message text out of a non-streaming ChatCompletion."""
    try:
        choices = response.choices
        if not choices:
            return ""
        message = choices[0].message
        content = getattr(message, "content", None)
        if isinstance(content, str):
            return content
        # Multi-modal content (list of parts) — concat text parts only.
        if isinstance(content, list):
            return "".join(
                part.get("text", "")
                for part in content
                if isinstance(part, dict) and part.get("type") == "text"
            )
        return ""
    except (AttributeError, IndexError, TypeError):
        return ""


def _extract_text_from_chunk(chunk: Any) -> str:
    """Pull the delta text out of a streaming ChatCompletionChunk."""
    try:
        choices = chunk.choices
        if not choices:
            return ""
        delta = choices[0].delta
        content = getattr(delta, "content", None)
        return content or ""
    except (AttributeError, IndexError, TypeError):
        return ""


# ── Client resolution ──────────────────────────────────────────────────────


def _resolve_clients(target: Any) -> list[Any]:
    """Find the OpenAI client(s) on the target.

    If the target is the openai module itself, look for the module-level
    ``OpenAI()`` instance via ``openai.OpenAI`` and warn (we won't patch a
    class — only instances).
    """
    # Case 1: the target IS a client instance (has chat.completions).
    if hasattr(target, "chat"):
        return [target]
    # Case 2: the target is the openai module. We can't usefully patch a
    # class; the user must instantiate a client first. We DO patch the
    # module-level ``openai.chat.completions.create`` if it exists (older
    # openai SDK).
    if hasattr(target, "chat") and hasattr(target.chat, "completions"):
        return [target]
    return []


def _get_completions_namespace(client: Any) -> Any | None:
    """Return ``client.chat.completions`` or None if not present."""
    try:
        return client.chat.completions
    except AttributeError:
        return None


def _is_async_client(client: Any) -> bool:
    """Heuristic: detect AsyncOpenAI clients."""
    cls_name = type(client).__name__
    return cls_name.startswith("Async")


__all__ = ["attach", "detach"]
