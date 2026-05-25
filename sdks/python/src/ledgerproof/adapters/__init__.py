"""Vendor-specific adapters that monkey-patch upstream AI SDKs to auto-issue receipts.

Adapters are intentionally thin. Each one:

1. Locates the relevant method(s) on the target SDK or client.
2. Wraps them with a side-effect that issues an LPR receipt.
3. Is idempotent (calling ``attach`` twice is a no-op).
4. Is reversible via ``detach``.
5. Fails open — if LedgerProof is unreachable, the user's call still succeeds.

The :func:`ledgerproof.attach` and :func:`ledgerproof.detach` functions are
dispatchers — they inspect the target and route to the right adapter.
"""

from __future__ import annotations

from typing import Any

from ..errors import ConfigurationError


def attach(target: Any, **kwargs: Any) -> None:
    """Dispatch to the right vendor adapter.

    Supported targets:

    - The ``openai`` module, or an ``openai.OpenAI`` / ``openai.AsyncOpenAI`` client.
    - (Coming soon) anthropic, google.generativeai, mistralai.

    :raises ConfigurationError: If the target's vendor is unrecognized.
    """
    vendor = _identify_vendor(target)
    if vendor == "openai":
        from . import openai as openai_adapter

        openai_adapter.attach(target, **kwargs)
        return
    if vendor == "anthropic":
        # Sprint 2.
        raise ConfigurationError(
            "Anthropic adapter not yet shipped in this SDK release. "
            "Use the direct LedgerProof.publish_ai_article_50() API for now. "
            "Track: https://github.com/vsdawkins-creator/ledgerproof-python/issues"
        )
    raise ConfigurationError(
        f"Don't know how to attach to {target!r}. "
        f"Pass the openai module or an openai client. "
        f"For other AI providers, use LedgerProof.publish_ai_article_50() directly."
    )


def detach(target: Any) -> None:
    """Reverse the monkey-patching applied by :func:`attach`. Idempotent."""
    vendor = _identify_vendor(target)
    if vendor == "openai":
        from . import openai as openai_adapter

        openai_adapter.detach(target)
        return
    # Unknown target — silently no-op (matches detach idempotency contract).


def _identify_vendor(target: Any) -> str | None:
    """Inspect the target object to determine which adapter to use."""
    module = getattr(target, "__module__", None) or getattr(
        getattr(target, "__class__", None), "__module__", ""
    )
    name = getattr(target, "__name__", "")
    if module is None:
        module = ""

    if module.startswith("openai") or name == "openai" or "OpenAI" in type(target).__name__:
        return "openai"
    if module.startswith("anthropic") or name == "anthropic":
        return "anthropic"
    if module.startswith("google.generativeai") or name == "google.generativeai":
        return "google"
    if module.startswith("mistralai") or name == "mistralai":
        return "mistral"
    return None


__all__ = ["attach", "detach"]
