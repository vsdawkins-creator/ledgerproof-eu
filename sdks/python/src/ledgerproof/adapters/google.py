"""Google Gemini SDK adapter (google-generativeai).

Wraps ``GenerativeModel.generate_content`` (sync + async + streaming).
The Gemini response has ``response.text`` (a property that concatenates
the text parts).

Usage::

    import google.generativeai as genai
    import ledgerproof

    genai.configure(api_key="...")
    model = genai.GenerativeModel("gemini-1.5-pro")
    ledgerproof.attach(
        model,
        publisher_id="LEI:...",
        deployer_country="DE",
        deployer_name="Acme Corp",
    )

    response = model.generate_content("Write a haiku.")
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

logger = logging.getLogger("ledgerproof.adapters.google")

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
    """Patch a Gemini ``GenerativeModel`` instance to auto-issue receipts."""
    if not hasattr(target, "generate_content"):
        raise LedgerProofError(
            f"Could not locate a Gemini GenerativeModel on {target!r}."
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
    executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="ledgerproof-google")
    model_name = getattr(target, "model_name", "gemini/unknown")
    settings = {
        "lp": lp,
        "executor": executor,
        "deployer_name": deployer_name,
        "ai_system_id_override": ai_system_id,
        "model_name": model_name,
        "is_public_interest": is_public_interest,
    }

    original = target.generate_content
    target.generate_content = _wrap(original, settings)
    _PATCHED[key] = {"target": target, "original": original, "settings": settings}
    logger.info("Attached LedgerProof to Gemini model %s.", model_name)


def detach(target: Any) -> None:
    info = _PATCHED.pop(id(target), None)
    if info is None:
        return
    info["target"].generate_content = info["original"]
    info["settings"]["executor"].shutdown(wait=False)


def _wrap(original: Callable[..., Any], settings: dict[str, Any]) -> Callable[..., Any]:
    @functools.wraps(original)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        response = original(*args, **kwargs)
        # Streaming returns an iterator; non-streaming returns a GenerateContentResponse.
        if hasattr(response, "__iter__") and not hasattr(response, "text"):
            return _wrap_stream(response, settings)
        text = _extract_text(response)
        if text:
            _schedule_receipt(text, settings, response)
        return response

    return wrapped


def _wrap_stream(stream: Any, settings: dict[str, Any]) -> Any:
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
                    _schedule_receipt(full, settings, stream)
                raise
            text = _extract_text(chunk)
            if text:
                chunks.append(text)
            return chunk

        def __getattr__(self, name: str) -> Any:
            return getattr(stream, name)

    return _StreamWrapper()


def _schedule_receipt(text: str, settings: dict[str, Any], response: Any) -> None:
    executor: ThreadPoolExecutor = settings["executor"]
    future: Future[Receipt | None] = executor.submit(_issue_safe, text, settings)
    try:
        response._ledgerproof_future = future  # type: ignore[attr-defined]
    except (AttributeError, TypeError):
        pass


def _issue_safe(text: str, settings: dict[str, Any]) -> Any:
    try:
        lp: LedgerProof = settings["lp"]
        ai_system_id = settings["ai_system_id_override"] or f"google/{settings['model_name']}"
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
    """Gemini: ``response.text`` is a convenience that joins all text parts."""
    try:
        text = response.text
        return text if isinstance(text, str) else ""
    except (AttributeError, ValueError):
        # ValueError raised by google-generativeai when parts is empty.
        try:
            candidates = response.candidates
            if not candidates:
                return ""
            parts = candidates[0].content.parts
            return "".join(getattr(p, "text", "") for p in parts)
        except (AttributeError, IndexError):
            return ""


__all__ = ["attach", "detach"]
