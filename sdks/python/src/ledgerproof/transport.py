"""HTTP transport for talking to LedgerProof operators.

Wraps ``httpx`` with retry/backoff, structured logging, error mapping, and a
sync/async pair that share a single implementation.

Design notes:

- One :class:`Transport` instance per :class:`~ledgerproof.client.LedgerProof`.
- Transport owns the ``httpx.Client`` and ``httpx.AsyncClient`` lifecycle;
  the client borrows them.
- Retries: 3 attempts on 429/502/503/504/network error, exponential backoff
  (250ms → 500ms → 1s), honoring ``Retry-After``.
- Timeouts: 10s connect, 30s read by default. Configurable per-request.
- User-Agent: ``ledgerproof-python/{version} ({platform})``.
- Never logs the API key or any request body containing secrets.
"""

from __future__ import annotations

import asyncio
import logging
import platform
import sys
import time
from typing import TYPE_CHECKING, Any

import httpx

from ._version import __version__
from .errors import (
    APIError,
    AuthenticationError,
    NetworkError,
    RateLimitError,
    ValidationError,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

logger = logging.getLogger("ledgerproof.transport")

_DEFAULT_TIMEOUT = httpx.Timeout(connect=10.0, read=30.0, write=30.0, pool=10.0)
_DEFAULT_MAX_RETRIES = 3
_RETRYABLE_STATUS = frozenset({429, 502, 503, 504})


def _user_agent() -> str:
    """Build the User-Agent header. Python version, platform, SDK version."""
    py = f"Python/{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    plat = platform.system()
    return f"ledgerproof-python/{__version__} ({py}; {plat})"


def _backoff_delay(attempt: int, retry_after: str | None) -> float:
    """Compute the next retry delay in seconds.

    Honors a server-provided ``Retry-After`` header if present and numeric.
    Otherwise uses exponential backoff: 0.25s, 0.5s, 1.0s.

    :param attempt: 0-indexed retry attempt number.
    :param retry_after: Value of the ``Retry-After`` response header, if any.
    """
    if retry_after:
        try:
            return min(float(retry_after), 30.0)
        except ValueError:
            pass
    return min(0.25 * (2**attempt), 30.0)


def _raise_for_response(response: httpx.Response) -> None:
    """Map an HTTP response to an SDK exception.

    Called only when the response is non-2xx. 4xx errors map to specific
    exceptions; 5xx maps to :class:`APIError`. The retry policy is applied
    by the caller — this function just classifies the final response.
    """
    request_id = response.headers.get("x-request-id")
    status = response.status_code
    try:
        body_text = response.text
    except Exception:  # pragma: no cover
        body_text = "<unable to decode body>"

    # Try to extract a structured error message from the body.
    try:
        body_json = response.json()
        message = (
            body_json.get("error", {}).get("message")
            if isinstance(body_json, dict)
            else None
        ) or body_text
    except Exception:
        message = body_text

    ctx = {"status": status, "request_id": request_id, "url": str(response.url)}

    if status in (401, 403):
        raise AuthenticationError(message, context=ctx)
    if status == 429:
        retry_after = response.headers.get("retry-after")
        retry_seconds: float | None = None
        if retry_after:
            try:
                retry_seconds = float(retry_after)
            except ValueError:
                retry_seconds = None
        raise RateLimitError(
            message, retry_after_seconds=retry_seconds, context=ctx
        )
    if status in (400, 422):
        # Try to extract field-level errors for validation issues.
        errors: list[dict[str, Any]] = []
        try:
            body_json = response.json()
            if isinstance(body_json, dict) and "errors" in body_json:
                raw_errors = body_json["errors"]
                if isinstance(raw_errors, list):
                    errors = [e for e in raw_errors if isinstance(e, dict)]
        except Exception:
            pass
        raise ValidationError(message, errors=errors, context=ctx)

    raise APIError(message, status_code=status, body=body_text, request_id=request_id, context=ctx)


class Transport:
    """Sync HTTP transport. Owns a single :class:`httpx.Client`.

    Use the parent :class:`~ledgerproof.client.LedgerProof` rather than
    instantiating this directly.
    """

    def __init__(
        self,
        *,
        api_base: str,
        api_key: str | None = None,
        publisher_id: str | None = None,
        timeout: httpx.Timeout = _DEFAULT_TIMEOUT,
        max_retries: int = _DEFAULT_MAX_RETRIES,
        client: httpx.Client | None = None,
    ) -> None:
        self._api_base = api_base.rstrip("/")
        self._api_key = api_key
        self._publisher_id = publisher_id
        self._max_retries = max_retries
        self._owned_client = client is None
        self._client = client or httpx.Client(
            timeout=timeout,
            headers={"User-Agent": _user_agent()},
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        json: Any | None = None,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        timeout: httpx.Timeout | None = None,
        authenticated: bool = True,
    ) -> Any:
        """Send a request, retrying on retriable statuses.

        Returns the parsed JSON response on success. Raises an SDK
        exception on failure.

        :param method: HTTP method ("GET", "POST", "DELETE", ...).
        :param path: Path relative to the API base (e.g., ``/v1/publish``).
        :param json: Body to JSON-encode.
        :param params: Query string parameters.
        :param headers: Extra headers to merge with defaults.
        :param timeout: Per-request timeout override.
        :param authenticated: If True, attach API-key headers. Set False
            for unauthenticated public endpoints (verify, lookup).
        """
        url = f"{self._api_base}{path}"
        merged_headers = dict(headers or {})
        if authenticated:
            if not self._api_key or not self._publisher_id:
                from .errors import ConfigurationError

                raise ConfigurationError(
                    "API key and publisher_id required for authenticated requests"
                )
            merged_headers["X-Api-Key"] = self._api_key
            merged_headers["X-Publisher-Id"] = self._publisher_id

        last_error: Exception | None = None
        for attempt in range(self._max_retries + 1):
            try:
                response = self._client.request(
                    method,
                    url,
                    json=json,
                    params=params,
                    headers=merged_headers,
                    timeout=timeout,
                )
            except httpx.TimeoutException as exc:
                last_error = exc
                if attempt < self._max_retries:
                    time.sleep(_backoff_delay(attempt, None))
                    continue
                raise NetworkError(
                    f"request to {url} timed out after {self._max_retries + 1} attempts",
                    context={"url": url, "cause": str(exc)},
                ) from exc
            except httpx.NetworkError as exc:
                last_error = exc
                if attempt < self._max_retries:
                    time.sleep(_backoff_delay(attempt, None))
                    continue
                raise NetworkError(
                    f"network error contacting {url}: {exc}",
                    context={"url": url},
                ) from exc

            if 200 <= response.status_code < 300:
                if response.status_code == 204:
                    return None
                return response.json()

            if response.status_code in _RETRYABLE_STATUS and attempt < self._max_retries:
                delay = _backoff_delay(attempt, response.headers.get("retry-after"))
                logger.warning(
                    "transient %s from %s; retrying in %.2fs (attempt %d/%d)",
                    response.status_code, url, delay, attempt + 1, self._max_retries,
                )
                time.sleep(delay)
                continue

            _raise_for_response(response)

        # Should be unreachable; appease the type checker.
        raise NetworkError(  # pragma: no cover
            f"exhausted retries to {url}",
            context={"cause": str(last_error) if last_error else "unknown"},
        )

    def close(self) -> None:
        """Close the underlying httpx client if we own it."""
        if self._owned_client:
            self._client.close()

    def __enter__(self) -> Transport:
        return self

    def __exit__(self, *exc_info: Any) -> None:
        self.close()


class AsyncTransport:
    """Async counterpart to :class:`Transport`. Same contract, ``await``-able."""

    def __init__(
        self,
        *,
        api_base: str,
        api_key: str | None = None,
        publisher_id: str | None = None,
        timeout: httpx.Timeout = _DEFAULT_TIMEOUT,
        max_retries: int = _DEFAULT_MAX_RETRIES,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._api_base = api_base.rstrip("/")
        self._api_key = api_key
        self._publisher_id = publisher_id
        self._max_retries = max_retries
        self._owned_client = client is None
        self._client = client or httpx.AsyncClient(
            timeout=timeout,
            headers={"User-Agent": _user_agent()},
        )

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: Any | None = None,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        timeout: httpx.Timeout | None = None,
        authenticated: bool = True,
    ) -> Any:
        """Async version of :meth:`Transport.request`. Same semantics."""
        url = f"{self._api_base}{path}"
        merged_headers = dict(headers or {})
        if authenticated:
            if not self._api_key or not self._publisher_id:
                from .errors import ConfigurationError

                raise ConfigurationError(
                    "API key and publisher_id required for authenticated requests"
                )
            merged_headers["X-Api-Key"] = self._api_key
            merged_headers["X-Publisher-Id"] = self._publisher_id

        last_error: Exception | None = None
        for attempt in range(self._max_retries + 1):
            try:
                response = await self._client.request(
                    method,
                    url,
                    json=json,
                    params=params,
                    headers=merged_headers,
                    timeout=timeout,
                )
            except httpx.TimeoutException as exc:
                last_error = exc
                if attempt < self._max_retries:
                    await asyncio.sleep(_backoff_delay(attempt, None))
                    continue
                raise NetworkError(
                    f"request to {url} timed out after {self._max_retries + 1} attempts",
                    context={"url": url, "cause": str(exc)},
                ) from exc
            except httpx.NetworkError as exc:
                last_error = exc
                if attempt < self._max_retries:
                    await asyncio.sleep(_backoff_delay(attempt, None))
                    continue
                raise NetworkError(
                    f"network error contacting {url}: {exc}",
                    context={"url": url},
                ) from exc

            if 200 <= response.status_code < 300:
                if response.status_code == 204:
                    return None
                return response.json()

            if response.status_code in _RETRYABLE_STATUS and attempt < self._max_retries:
                delay = _backoff_delay(attempt, response.headers.get("retry-after"))
                logger.warning(
                    "transient %s from %s; retrying in %.2fs (attempt %d/%d)",
                    response.status_code, url, delay, attempt + 1, self._max_retries,
                )
                await asyncio.sleep(delay)
                continue

            _raise_for_response(response)

        raise NetworkError(  # pragma: no cover
            f"exhausted retries to {url}",
            context={"cause": str(last_error) if last_error else "unknown"},
        )

    async def aclose(self) -> None:
        """Close the underlying httpx client if we own it."""
        if self._owned_client:
            await self._client.aclose()

    async def __aenter__(self) -> AsyncTransport:
        return self

    async def __aexit__(self, *exc_info: Any) -> None:
        await self.aclose()


__all__ = ["AsyncTransport", "Transport"]
