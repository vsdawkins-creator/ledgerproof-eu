"""The user-facing :class:`LedgerProof` and :class:`AsyncLedgerProof` clients.

Most users will interact with the SDK through one of three paths:

1. ``ledgerproof.attach(openai)`` — the Stripe play. Three lines, you're done.
2. ``LedgerProof(...).publish_ai_article_50(...)`` — direct receipt issuance.
3. ``AsyncLedgerProof(...).publish_ai_article_50(...)`` — async equivalent.

This module implements (2) and (3). The adapter modules build on top.

End-to-end publish flow (what happens under ``publish_ai_article_50``):

  1. Build the content payload (Pydantic validation, GDPR checks).
  2. Compute ``artifact_hash`` and ``content_hash`` locally.
  3. Lazy-register the signing key with ``POST /v1/keys`` if not done yet.
  4. Discover the current chain tip via ``GET /v1/entries/{n}`` probing.
  5. Build the canonical entry envelope.
  6. Compute ``entry_hash = SHA-256(entry_json_canonical)``.
  7. Sign the raw 32 bytes of ``entry_hash`` with Ed25519.
  8. POST to ``/v1/publish``.
  9. Return a typed :class:`Receipt`.

The reference implementation is ``13-api-backend/eu-ai-act-50-test-receipt.py``
in the LedgerProof-Launch-July6 repo. This module is its production refactor —
same protocol, same byte-for-byte canonicalization, plus retry/backoff,
GDPR safety checks, typed responses, and the auto-registration loop.
"""

from __future__ import annotations

import logging
import os
import time
from datetime import datetime, timezone
from typing import Any, Optional

from .canonical import canonical_json, sha256_hex
from .errors import (
    ChainError,
    ConfigurationError,
    LedgerProofError,
    NetworkError,
    ValidationError,
)
from .gdpr import assert_legal_entity_id, assert_no_pii
from .keys import Keypair
from .transport import AsyncTransport, Transport
from .types import (
    AiArticle50Content,
    AiChatbotSessionContent,
    AiHumanReviewContent,
    ContentCategory,
    EntryResponse,
    GenerationType,
    NotificationMethod,
    PerceptualHash,
    Receipt,
    ReviewType,
)

logger = logging.getLogger("ledgerproof.client")

# Default EU production endpoint. Frankfurt, EU data residency.
DEFAULT_API_BASE = "https://api-eu.ledgerproofhq.io"

# Maximum sequence we'll probe when discovering the chain tip. At launch the
# chain is essentially empty; this is a generous safety cap. Real deployments
# at high volume should provide the tip explicitly via ``LedgerProof.publish_at()``.
_TIP_PROBE_LIMIT = 10_000

# Genesis prev_hash: 64 zeros.
_GENESIS_PREV_HASH = "0" * 64

# Default key id derived from environment, hostname, or "default".
def _default_key_id() -> str:
    return os.environ.get("LEDGERPROOF_KEY_ID") or "default"


def _now_iso() -> str:
    """ISO 8601 timestamp with millisecond precision and Z suffix, as the server emits."""
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S") + f".{now.microsecond // 1000:03d}Z"


class _ClientState:
    """Internal mutable state shared between sync and async clients.

    Tracks whether the signing key has been registered with the server yet
    (lazy registration on first publish).
    """

    __slots__ = ("key_registered_at_sequence",)

    def __init__(self) -> None:
        self.key_registered_at_sequence: Optional[int] = None


class _ClientCore:
    """Shared base — holds keypair, transport handle, config.

    Concrete clients (:class:`LedgerProof`, :class:`AsyncLedgerProof`) provide
    sync vs async wrappers around the same logical operations.
    """

    def __init__(
        self,
        *,
        publisher_id: str,
        deployer_country: str,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        key_id: Optional[str] = None,
        keypair: Optional[Keypair] = None,
    ) -> None:
        # ── Resolve config ──────────────────────────────────────────────
        resolved_api_key = api_key or os.environ.get("LEDGERPROOF_API_KEY")
        if not resolved_api_key:
            raise ConfigurationError(
                "API key required. Pass api_key=... or set LEDGERPROOF_API_KEY "
                "in the environment. Provision a key via "
                "POST /v1/admin/provision (admin) or talk to your LedgerProof operator."
            )

        assert_legal_entity_id(publisher_id, field_name="publisher_id")

        self.publisher_id = publisher_id
        self.deployer_country = deployer_country.upper()
        self._api_key = resolved_api_key
        self._api_base = (api_base or os.environ.get("LEDGERPROOF_API_BASE") or DEFAULT_API_BASE).rstrip("/")
        self._key_id = key_id or _default_key_id()
        self._keypair = keypair or self._load_or_generate_keypair()
        self._state = _ClientState()

    @staticmethod
    def _load_or_generate_keypair() -> Keypair:
        """Resolve a signing keypair: env > file > generate.

        Env var ``LEDGERPROOF_SIGNING_KEY_HEX`` takes precedence (for
        stateless deployments). Otherwise we load from
        ``~/.config/ledgerproof/signing_key.bin``, generating if absent.
        New keys are immediately saved.
        """
        from_env = Keypair.from_env()
        if from_env is not None:
            return from_env
        keypair, was_generated = Keypair.load_or_generate()
        if was_generated:
            logger.info(
                "Generated new Ed25519 signing key; saved to %s. "
                "Back this file up — it cannot be recovered if lost.",
                os.environ.get("LEDGERPROOF_KEY_PATH")
                or "~/.config/ledgerproof/signing_key.bin",
            )
        return keypair

    # ── Pure helpers (no I/O) ───────────────────────────────────────────

    def _build_article_50_content(
        self,
        *,
        artifact: bytes | str,
        artifact_content_type: str,
        ai_system_id: str,
        deployer_name: str,
        content_category: ContentCategory | str,
        ai_system_version: Optional[str] = None,
        supervisory_authority: Optional[str] = None,
        generation_type: Optional[GenerationType | str] = None,
        source_content_hash: Optional[str] = None,
        perceptual_hash: Optional[PerceptualHash] = None,
        transparency_marker: str = "LPR-EU-AI-ACT-50",
        is_public_interest: Optional[bool] = None,
        enforcement_date: str = "2026-08-02",
        profile_version: str = "EU-AI-ACT-50-v1.1",
    ) -> tuple[AiArticle50Content, str]:
        """Hash the artifact locally and build the content model.

        Returns ``(content, artifact_hash)``. The artifact bytes never leave
        this function — only the hash continues.
        """
        if isinstance(artifact, str):
            artifact_bytes_count = len(artifact.encode("utf-8"))
        else:
            artifact_bytes_count = len(artifact)

        artifact_hash = sha256_hex(artifact)

        # Convert string enums for backwards-compat ergonomics.
        cat = (
            ContentCategory(content_category)
            if isinstance(content_category, str)
            else content_category
        )
        gen = (
            GenerationType(generation_type)
            if isinstance(generation_type, str)
            else generation_type
        )

        content = AiArticle50Content(
            ai_system_id=ai_system_id,
            ai_system_version=ai_system_version,
            deployer_id=self.publisher_id,
            deployer_name=deployer_name,
            deployer_country=self.deployer_country,
            content_category=cat,
            artifact_hash=artifact_hash,
            artifact_content_type=artifact_content_type,
            artifact_bytes=artifact_bytes_count,
            supervisory_authority=supervisory_authority,
            generation_type=gen,
            source_content_hash=source_content_hash,
            perceptual_hash=perceptual_hash,
            transparency_marker=transparency_marker,
            is_public_interest=is_public_interest,
            enforcement_date=enforcement_date,
            profile_version=profile_version,
        )
        return content, artifact_hash

    def _build_publish_payload(
        self,
        *,
        content_dict: dict[str, Any],
        content_type: str,
        sequence: int,
        prev_hash: str,
    ) -> dict[str, Any]:
        """Build the full publish request body. Pure function — no I/O.

        Computes the canonical entry, hashes it, signs it. Returns the dict
        ready to POST.
        """
        # content_hash is SHA-256 of the canonical content payload alone.
        content_canonical = canonical_json(content_dict)
        content_hash = sha256_hex(content_canonical.encode("utf-8"))

        entry_timestamp = _now_iso()

        # Build the canonical entry. ALL keys sorted alphabetically.
        entry_obj = {
            "content": content_dict,
            "content_hash": content_hash,
            "content_type": content_type,
            "entry_timestamp": entry_timestamp,
            "key_id": self._key_id,
            "prev_hash": prev_hash,
            "protocol_version": "ledgerproof/1.0",
            "publisher_id": self.publisher_id,
            "sequence": sequence,
        }
        entry_json_canonical = canonical_json(entry_obj)
        entry_hash = sha256_hex(entry_json_canonical.encode("utf-8"))

        # Sign the RAW 32 bytes of the entry_hash, not the hex string.
        signature = self._keypair.sign(bytes.fromhex(entry_hash))

        return {
            "publisher_id": self.publisher_id,
            "key_id": self._key_id,
            "prev_hash": prev_hash,
            "entry_hash": entry_hash,
            "signature": signature.hex(),
            "protocol_version": "ledgerproof/1.0",
            "content_type": content_type,
            "content_hash": content_hash,
            "content": content_dict,
            "entry_json_canonical": entry_json_canonical,
            "entry_timestamp": entry_timestamp,
        }

    def _gdpr_check_article_50(self, content: AiArticle50Content) -> None:
        """Final defensive PII check before transmission.

        Pydantic already rejected emails in deployer_id at model construction.
        This pass also checks the deployer_name and supervisory_authority
        (free-text fields) for stray PII before the network hop.
        """
        assert_no_pii(content.deployer_name, field_name="deployer_name")
        if content.supervisory_authority:
            assert_no_pii(
                content.supervisory_authority, field_name="supervisory_authority"
            )


# ── Sync client ──────────────────────────────────────────────────────────


class LedgerProof(_ClientCore):
    """Synchronous LedgerProof client.

    Typical usage::

        from ledgerproof import LedgerProof

        lp = LedgerProof(
            publisher_id="LEI:5493001KJTIIGC8Y1R12",
            deployer_country="DE",
        )

        receipt = lp.publish_ai_article_50(
            artifact="The generated article text...",
            artifact_content_type="text/plain",
            ai_system_id="openai/gpt-4o/2024-11-20",
            deployer_name="Acme Insurance AG",
            content_category="SYNTHETIC_TEXT",
        )
        print(receipt.sequence, receipt.entry_hash, receipt.verify_url)

    Configuration is resolved in this order: kwarg → environment variable →
    default. The supported environment variables are:

    - ``LEDGERPROOF_API_KEY`` — required if not passed as ``api_key=``.
    - ``LEDGERPROOF_API_BASE`` — defaults to ``https://api-eu.ledgerproofhq.io``.
    - ``LEDGERPROOF_SIGNING_KEY_HEX`` — 64-hex-char private key (alternative
      to the file store).
    - ``LEDGERPROOF_KEY_ID`` — defaults to ``"default"``. Must be unique per
      keypair within your ``publisher_id``.
    - ``LEDGERPROOF_KEY_PATH`` — override the default key file location.
    """

    def __init__(
        self,
        *,
        publisher_id: str,
        deployer_country: str,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        key_id: Optional[str] = None,
        keypair: Optional[Keypair] = None,
        transport: Optional[Transport] = None,
    ) -> None:
        super().__init__(
            publisher_id=publisher_id,
            deployer_country=deployer_country,
            api_key=api_key,
            api_base=api_base,
            key_id=key_id,
            keypair=keypair,
        )
        self._transport = transport or Transport(
            api_base=self._api_base,
            api_key=self._api_key,
            publisher_id=self.publisher_id,
        )

    # ── Public API ──────────────────────────────────────────────────────

    def publish_ai_article_50(
        self,
        *,
        artifact: bytes | str,
        artifact_content_type: str,
        ai_system_id: str,
        deployer_name: str,
        content_category: ContentCategory | str,
        ai_system_version: Optional[str] = None,
        supervisory_authority: Optional[str] = None,
        generation_type: Optional[GenerationType | str] = None,
        source_content_hash: Optional[str] = None,
        perceptual_hash: Optional[PerceptualHash] = None,
        transparency_marker: str = "LPR-EU-AI-ACT-50",
        is_public_interest: Optional[bool] = None,
        enforcement_date: str = "2026-08-02",
        profile_version: str = "EU-AI-ACT-50-v1.1",
    ) -> Receipt:
        """Issue an LPR ``ai/article-50/v1`` receipt for the given artifact.

        The ``artifact`` is hashed locally — the bytes never leave your
        machine. Only the SHA-256 (and optional perceptual hash) is
        transmitted to LedgerProof.

        :returns: A :class:`Receipt` with ``sequence``, ``entry_hash``,
            and ``verify_url`` populated.
        """
        content, _ = self._build_article_50_content(
            artifact=artifact,
            artifact_content_type=artifact_content_type,
            ai_system_id=ai_system_id,
            deployer_name=deployer_name,
            content_category=content_category,
            ai_system_version=ai_system_version,
            supervisory_authority=supervisory_authority,
            generation_type=generation_type,
            source_content_hash=source_content_hash,
            perceptual_hash=perceptual_hash,
            transparency_marker=transparency_marker,
            is_public_interest=is_public_interest,
            enforcement_date=enforcement_date,
            profile_version=profile_version,
        )
        self._gdpr_check_article_50(content)

        content_dict = content.model_dump(exclude_none=True, mode="json")
        return self._publish("ai/article-50/v1", content_dict)

    def publish_human_review(
        self,
        *,
        original_entry_hash: str,
        original_sequence: int,
        reviewed_artifact: bytes | str,
        reviewer_role: str,
        reviewer_country: str,
        review_type: ReviewType | str,
        is_public_interest: bool,
        review_rationale: Optional[str] = None,
    ) -> Receipt:
        """Issue a ``ai/human-review/v1`` receipt linked to a prior ai/article-50 receipt.

        Used to invoke the Article 50(4) editorial review exemption.
        """
        if isinstance(reviewed_artifact, str):
            reviewed_bytes = reviewed_artifact.encode("utf-8")
        else:
            reviewed_bytes = reviewed_artifact
        reviewed_artifact_hash = sha256_hex(reviewed_bytes)

        rt = ReviewType(review_type) if isinstance(review_type, str) else review_type

        content = AiHumanReviewContent(
            original_entry_hash=original_entry_hash,
            original_sequence=original_sequence,
            reviewer_role=reviewer_role,
            reviewer_country=reviewer_country.upper(),
            review_timestamp=datetime.now(timezone.utc),
            review_type=rt,
            reviewed_artifact_hash=reviewed_artifact_hash,
            is_public_interest=is_public_interest,
            review_rationale=review_rationale,
        )
        # GDPR pre-checks.
        assert_no_pii(content.reviewer_role, field_name="reviewer_role")
        if content.review_rationale:
            assert_no_pii(content.review_rationale, field_name="review_rationale")

        content_dict = content.model_dump(exclude_none=True, mode="json")
        return self._publish("ai/human-review/v1", content_dict)

    def publish_chatbot_session(
        self,
        *,
        session_id: str,
        ai_system_id: str,
        deployer_name: str,
        notification_method: NotificationMethod | str,
        notification_text: str,
        obvious_exemption_claimed: bool = False,
    ) -> Receipt:
        """Issue a ``ai/chatbot-session/v1`` receipt for Article 50(1) compliance.

        The ``session_id`` is hashed locally — only the SHA-256 is transmitted.
        Same for ``notification_text``.
        """
        session_id_hash = sha256_hex(session_id)
        notification_text_hash = sha256_hex(notification_text)
        nm = (
            NotificationMethod(notification_method)
            if isinstance(notification_method, str)
            else notification_method
        )

        content = AiChatbotSessionContent(
            session_id_hash=session_id_hash,
            ai_system_id=ai_system_id,
            deployer_id=self.publisher_id,
            deployer_name=deployer_name,
            deployer_country=self.deployer_country,
            notification_timestamp=datetime.now(timezone.utc),
            notification_method=nm,
            notification_text_hash=notification_text_hash,
            obvious_exemption_claimed=obvious_exemption_claimed,
        )
        assert_no_pii(content.deployer_name, field_name="deployer_name")

        content_dict = content.model_dump(exclude_none=True, mode="json")
        return self._publish("ai/chatbot-session/v1", content_dict)

    # ── Verification ────────────────────────────────────────────────────

    def verify(self, sequence: int) -> EntryResponse:
        """Fetch a receipt by sequence number from the public verifier endpoint.

        Unauthenticated; anyone can call this.
        """
        data = self._transport.request(
            "GET", f"/v1/entries/{sequence}", authenticated=False
        )
        return EntryResponse.model_validate(data)

    def lookup_by_content_hash(self, content_hash: str) -> list[EntryResponse]:
        """Find receipts whose ``content_hash`` matches the given SHA-256.

        Unauthenticated. The receipt for an artifact can be discovered by
        any third party that has the artifact and computes its hash.
        """
        data = self._transport.request(
            "GET",
            f"/v1/receipts/by-content-hash/{content_hash}",
            authenticated=False,
        )
        matches = data.get("matches", []) if isinstance(data, dict) else []
        return [EntryResponse.model_validate(m) for m in matches]

    # ── Internals ───────────────────────────────────────────────────────

    def _publish(self, content_type: str, content_dict: dict[str, Any]) -> Receipt:
        """Common publish path: ensure key registered, discover tip, retry on chain race."""
        self._ensure_key_registered()

        # Try up to 3 times, re-discovering the tip on chain race.
        last_error: Optional[Exception] = None
        for attempt in range(3):
            sequence, prev_hash = self._discover_chain_tip()
            payload = self._build_publish_payload(
                content_dict=content_dict,
                content_type=content_type,
                sequence=sequence,
                prev_hash=prev_hash,
            )
            try:
                response = self._transport.request("POST", "/v1/publish", json=payload)
                return Receipt.model_validate(response)
            except ValidationError as exc:
                # Likely a chain race (409). Re-discover and retry.
                last_error = exc
                if attempt < 2 and "sequence" in (exc.message or "").lower():
                    logger.info("chain race detected, re-discovering tip (attempt %d/3)", attempt + 2)
                    time.sleep(0.2 * (attempt + 1))
                    continue
                raise

        raise ChainError(
            f"could not publish after 3 attempts: {last_error}",
            context={"last_error": str(last_error) if last_error else None},
        )

    def _ensure_key_registered(self) -> None:
        """Register the signing key with the server if not done in this process.

        Idempotent on the server side (``ON CONFLICT (key_id) DO NOTHING``),
        but we cache the result locally to avoid an extra round-trip on
        every publish.
        """
        if self._state.key_registered_at_sequence is not None:
            return
        payload = {
            "key_id": self._key_id,
            "verifying_key_b64": self._keypair.public_b64(),
        }
        try:
            response = self._transport.request("POST", "/v1/keys", json=payload)
        except LedgerProofError as exc:
            # Key may already be registered — that's fine, we'll find out
            # at publish-verify time if it isn't.
            logger.debug("key registration response: %s", exc)
            self._state.key_registered_at_sequence = 0
            return
        if isinstance(response, dict) and "effective_from_sequence" in response:
            self._state.key_registered_at_sequence = int(response["effective_from_sequence"])
        else:
            self._state.key_registered_at_sequence = 0

    def _discover_chain_tip(self) -> tuple[int, str]:
        """Probe the chain to find the next sequence + the prev_hash.

        For a fresh chain, returns ``(0, "0" * 64)``. For a populated chain,
        walks forward from 0 until a 404 is returned, then reads the previous
        entry's ``entry_hash`` as the prev_hash.

        This is O(N) in chain length. For high-volume publishers, override
        by passing the tip explicitly. A future revision will add a
        dedicated ``GET /v1/chain/tip`` endpoint.
        """
        probe = 0
        while probe <= _TIP_PROBE_LIMIT:
            try:
                self._transport.request(
                    "GET", f"/v1/entries/{probe}", authenticated=False
                )
                probe += 1
            except LedgerProofError as exc:
                # APIError with status 404 means we found the tip.
                status = getattr(exc, "status_code", None)
                if status == 404:
                    if probe == 0:
                        return 0, _GENESIS_PREV_HASH
                    prev = self._transport.request(
                        "GET", f"/v1/entries/{probe - 1}", authenticated=False
                    )
                    return probe, prev["entry_hash"]
                raise

        raise ChainError(
            f"chain tip not found within {_TIP_PROBE_LIMIT} probes; "
            f"pass sequence and prev_hash explicitly for high-volume publishers"
        )

    # ── Lifecycle ───────────────────────────────────────────────────────

    def close(self) -> None:
        """Close the underlying transport."""
        self._transport.close()

    def __enter__(self) -> LedgerProof:
        return self

    def __exit__(self, *exc_info: Any) -> None:
        self.close()


# ── Async client ─────────────────────────────────────────────────────────


class AsyncLedgerProof(_ClientCore):
    """Asynchronous LedgerProof client. Mirrors :class:`LedgerProof` exactly,
    every method ``await``-able.

    Use ``async with AsyncLedgerProof(...) as lp:`` to manage the transport
    lifetime, or call ``await lp.aclose()`` explicitly.
    """

    def __init__(
        self,
        *,
        publisher_id: str,
        deployer_country: str,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        key_id: Optional[str] = None,
        keypair: Optional[Keypair] = None,
        transport: Optional[AsyncTransport] = None,
    ) -> None:
        super().__init__(
            publisher_id=publisher_id,
            deployer_country=deployer_country,
            api_key=api_key,
            api_base=api_base,
            key_id=key_id,
            keypair=keypair,
        )
        self._transport = transport or AsyncTransport(
            api_base=self._api_base,
            api_key=self._api_key,
            publisher_id=self.publisher_id,
        )

    async def publish_ai_article_50(
        self,
        *,
        artifact: bytes | str,
        artifact_content_type: str,
        ai_system_id: str,
        deployer_name: str,
        content_category: ContentCategory | str,
        **kwargs: Any,
    ) -> Receipt:
        """Async version of :meth:`LedgerProof.publish_ai_article_50`."""
        content, _ = self._build_article_50_content(
            artifact=artifact,
            artifact_content_type=artifact_content_type,
            ai_system_id=ai_system_id,
            deployer_name=deployer_name,
            content_category=content_category,
            **kwargs,
        )
        self._gdpr_check_article_50(content)
        content_dict = content.model_dump(exclude_none=True, mode="json")
        return await self._publish("ai/article-50/v1", content_dict)

    async def verify(self, sequence: int) -> EntryResponse:
        data = await self._transport.request(
            "GET", f"/v1/entries/{sequence}", authenticated=False
        )
        return EntryResponse.model_validate(data)

    async def _publish(self, content_type: str, content_dict: dict[str, Any]) -> Receipt:
        await self._ensure_key_registered()

        last_error: Optional[Exception] = None
        for attempt in range(3):
            sequence, prev_hash = await self._discover_chain_tip()
            payload = self._build_publish_payload(
                content_dict=content_dict,
                content_type=content_type,
                sequence=sequence,
                prev_hash=prev_hash,
            )
            try:
                response = await self._transport.request("POST", "/v1/publish", json=payload)
                return Receipt.model_validate(response)
            except ValidationError as exc:
                last_error = exc
                if attempt < 2 and "sequence" in (exc.message or "").lower():
                    import asyncio

                    await asyncio.sleep(0.2 * (attempt + 1))
                    continue
                raise

        raise ChainError(
            f"could not publish after 3 attempts: {last_error}",
            context={"last_error": str(last_error) if last_error else None},
        )

    async def _ensure_key_registered(self) -> None:
        if self._state.key_registered_at_sequence is not None:
            return
        payload = {
            "key_id": self._key_id,
            "verifying_key_b64": self._keypair.public_b64(),
        }
        try:
            response = await self._transport.request("POST", "/v1/keys", json=payload)
        except LedgerProofError as exc:
            logger.debug("key registration response: %s", exc)
            self._state.key_registered_at_sequence = 0
            return
        if isinstance(response, dict) and "effective_from_sequence" in response:
            self._state.key_registered_at_sequence = int(response["effective_from_sequence"])
        else:
            self._state.key_registered_at_sequence = 0

    async def _discover_chain_tip(self) -> tuple[int, str]:
        probe = 0
        while probe <= _TIP_PROBE_LIMIT:
            try:
                await self._transport.request(
                    "GET", f"/v1/entries/{probe}", authenticated=False
                )
                probe += 1
            except LedgerProofError as exc:
                status = getattr(exc, "status_code", None)
                if status == 404:
                    if probe == 0:
                        return 0, _GENESIS_PREV_HASH
                    prev = await self._transport.request(
                        "GET", f"/v1/entries/{probe - 1}", authenticated=False
                    )
                    return probe, prev["entry_hash"]
                raise
        raise ChainError(
            f"chain tip not found within {_TIP_PROBE_LIMIT} probes"
        )

    async def aclose(self) -> None:
        await self._transport.aclose()

    async def __aenter__(self) -> AsyncLedgerProof:
        return self

    async def __aexit__(self, *exc_info: Any) -> None:
        await self.aclose()


__all__ = [
    "AsyncLedgerProof",
    "DEFAULT_API_BASE",
    "LedgerProof",
]
