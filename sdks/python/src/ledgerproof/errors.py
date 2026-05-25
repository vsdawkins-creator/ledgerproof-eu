"""Exception hierarchy for the ledgerproof SDK.

All exceptions raised by the SDK derive from :class:`LedgerProofError`. Callers
may catch the base class to handle "anything went wrong with LedgerProof," or
catch specific subclasses to handle individual failure modes.

The SDK never raises a bare :class:`Exception` or :class:`ValueError` from
public code. If you see one, that's a bug — please file an issue.
"""

from __future__ import annotations

from typing import Any


class LedgerProofError(Exception):
    """Base class for every exception raised by the ledgerproof SDK.

    Catch this if you want to handle any LedgerProof failure uniformly without
    discriminating between subclasses.
    """

    def __init__(self, message: str, *, context: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.context: dict[str, Any] = context or {}

    def __str__(self) -> str:
        if self.context:
            ctx = ", ".join(f"{k}={v!r}" for k, v in self.context.items())
            return f"{self.message} ({ctx})"
        return self.message


class ConfigurationError(LedgerProofError):
    """Raised when the SDK is misconfigured (missing API key, bad publisher_id, etc.).

    Distinct from :class:`AuthenticationError`, which is raised by the *server*
    rejecting an otherwise well-formed credential.
    """


class AuthenticationError(LedgerProofError):
    """Server rejected the credentials (401/403 from /v1/publish or related).

    Usually means the API key is wrong, revoked, or doesn't match the
    publisher_id. Check ``LEDGERPROOF_API_KEY`` and ``LEDGERPROOF_PUBLISHER_ID``.
    """


class RateLimitError(LedgerProofError):
    """Server returned 429. ``retry_after_seconds`` is the server's hint.

    The transport already retries with backoff up to ``max_retries``; this
    exception is raised only after retries are exhausted.
    """

    def __init__(
        self,
        message: str,
        *,
        retry_after_seconds: float | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, context=context)
        self.retry_after_seconds = retry_after_seconds


class APIError(LedgerProofError):
    """Server returned a 4xx or 5xx response we didn't classify more specifically.

    ``status_code`` and ``body`` are populated. ``request_id`` is the server's
    correlation identifier if present in the response (``x-request-id`` header).
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        body: str | None = None,
        request_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, context=context)
        self.status_code = status_code
        self.body = body
        self.request_id = request_id


class NetworkError(LedgerProofError):
    """The SDK could not reach the server (DNS, timeout, connection refused, TLS).

    After the transport's retry budget is exhausted. Adapter code typically
    catches this and fails open (logs a warning, lets the user's call succeed
    without a receipt). Direct callers of :class:`LedgerProof` get this raised.
    """


class ValidationError(LedgerProofError):
    """The data did not pass client-side or server-side schema validation.

    Wraps Pydantic validation errors and server 422/400 responses about field
    shape. The ``errors`` attribute lists the offending fields if known.
    """

    def __init__(
        self,
        message: str,
        *,
        errors: list[dict[str, Any]] | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, context=context)
        self.errors: list[dict[str, Any]] = errors or []


class GDPRSafetyError(LedgerProofError):
    """The SDK detected what appears to be personal data and refused to transmit it.

    Raised by :mod:`ledgerproof.gdpr` before any network call. Catching this
    and bypassing the check requires re-implementing the check yourself — the
    SDK will not provide an opt-out. The intent is that personal data never
    leaves the user's machine via this SDK, by construction.

    See the LedgerProof GDPR Architecture document for the rationale.
    """


class KeyManagementError(LedgerProofError):
    """A key generation, load, save, or rotation operation failed.

    Wraps cryptography library errors and file-system permission errors on the
    signing key store.
    """


class ChainError(LedgerProofError):
    """The chain state is unexpected (e.g., prev_hash mismatch on publish).

    Almost always indicates a TOCTOU race where another publisher pushed an
    entry between our chain-tip discovery and our publish. The client retries
    automatically with the new tip; this exception is only raised if retry is
    disabled or exhausted.
    """


__all__ = [
    "APIError",
    "AuthenticationError",
    "ChainError",
    "ConfigurationError",
    "GDPRSafetyError",
    "KeyManagementError",
    "LedgerProofError",
    "NetworkError",
    "RateLimitError",
    "ValidationError",
]
