"""LangChain callback handler that emits LedgerProof transparency receipts.

Architectural invariants (do not violate):

  * Side-channel only. The handler MUST NOT modify the LLM response payload.
    All receipts go through the configured BaseEmitter.
  * Stream-aware signing. We commit to a transcript hash incrementally with
    `on_llm_new_token` and `on_llm_start`. We MUST NOT buffer the full body.
    `on_llm_end` finalizes the running SHA-256, canonical-CBOR-encodes the
    receipt, signs the digest, and emits.
  * Local verification only. The handler does not phone home.
"""

from __future__ import annotations

import base64
import hashlib
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.outputs import LLMResult

from .canonical import canonical_encode
from .emitter import BaseEmitter, LogEmitter
from .schema import SCHEMAS, get_schema
from .signer import BaseSigner, Ed25519Signer


@dataclass
class _RunState:
    """Per-run streaming hash state. One per LangChain `run_id`."""

    hasher: "hashlib._Hash"
    started_at: str
    model_identifier: str = "unknown"
    prompt_count: int = 0
    extra: Dict[str, Any] = field(default_factory=dict)


class LedgerProofCallbackHandler(BaseCallbackHandler):
    """Subclass of LangChain `BaseCallbackHandler` that emits signed receipts.

    Parameters
    ----------
    deployer_id:
        Pseudonymous identifier for the AI-system deployer. MUST NOT be an
        email address (the schema validator will reject it).
    schema:
        Receipt schema id. One of: 'chatbot_session/v1', 'generated_content/v1',
        'human_review/v1'. Defaults to 'chatbot_session/v1'.
    emitter:
        BaseEmitter implementation. Defaults to a LogEmitter writing to
        './ledgerproof-receipts.jsonl' in the current working directory.
    signer:
        BaseSigner implementation. Defaults to an ephemeral in-memory
        Ed25519Signer (MVP only — use an HSM signer in production).
    extra:
        Optional dict of additional fields merged into every receipt before
        validation (e.g. `model_identifier='gpt-4o-mini'`).
    """

    # LangChain looks at this attribute on streaming callbacks.
    always_verbose = True

    def __init__(
        self,
        deployer_id: str,
        schema: str = "chatbot_session/v1",
        emitter: Optional[BaseEmitter] = None,
        signer: Optional[BaseSigner] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        if schema not in SCHEMAS:
            raise ValueError(
                f"Unknown receipt schema: {schema!r}. Known: {sorted(SCHEMAS)}"
            )
        self.deployer_id = deployer_id
        self.schema_id = schema
        self.emitter: BaseEmitter = emitter or LogEmitter("./ledgerproof-receipts.jsonl")
        self.signer: BaseSigner = signer or Ed25519Signer()
        self.extra: Dict[str, Any] = dict(extra or {})
        self._runs: Dict[str, _RunState] = {}
        self._lock = threading.Lock()

    # ---------------------------------------------------------------- helpers

    def _run_key(self, run_id: Any) -> str:
        if isinstance(run_id, uuid.UUID):
            return str(run_id)
        return str(run_id) if run_id is not None else str(uuid.uuid4())

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")

    # ------------------------------------------------------------ LC callbacks

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: list[str],
        *,
        run_id: Optional[uuid.UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Commit transcript hash on stream start. Incrementally hash prompts.

        We deliberately hash prompts incrementally and discard them; we do
        not retain the prompt text.
        """
        key = self._run_key(run_id)
        h = hashlib.sha256()
        # Domain separator so prompts/tokens cannot collide across runs.
        h.update(b"lpr:v1:prompts\n")
        for p in prompts:
            h.update(len(p).to_bytes(8, "big"))
            h.update(p.encode("utf-8"))
        h.update(b"lpr:v1:tokens\n")

        # Best-effort model identifier extraction from LangChain's serialized payload.
        model_id = "unknown"
        if isinstance(serialized, dict):
            kwargs_ser = serialized.get("kwargs") or {}
            model_id = (
                kwargs_ser.get("model")
                or kwargs_ser.get("model_name")
                or serialized.get("name")
                or "unknown"
            )

        state = _RunState(
            hasher=h,
            started_at=self._utc_now(),
            model_identifier=str(model_id),
            prompt_count=len(prompts),
        )
        with self._lock:
            self._runs[key] = state

    def on_llm_new_token(
        self,
        token: str,
        *,
        run_id: Optional[uuid.UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Stream-aware hash update. Do NOT buffer tokens; just hash them."""
        key = self._run_key(run_id)
        with self._lock:
            state = self._runs.get(key)
        if state is None:
            return
        # Length-prefix each token for unambiguous reconstruction.
        b = token.encode("utf-8")
        state.hasher.update(len(b).to_bytes(8, "big"))
        state.hasher.update(b)

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: Optional[uuid.UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Finalize, build receipt, validate, sign, emit."""
        key = self._run_key(run_id)
        with self._lock:
            state = self._runs.pop(key, None)
        if state is None:
            # If start was never observed (e.g. handler attached mid-run),
            # start from an empty hash so we still emit a structurally
            # valid receipt rather than swallowing the event.
            state = _RunState(
                hasher=hashlib.sha256(b"lpr:v1:prompts\nlpr:v1:tokens\n"),
                started_at=self._utc_now(),
            )

        # If the LLM did not stream tokens, fold the final response text
        # into the hash now. This is the only place we touch the body, and
        # only to digest it — never to retain it.
        if response is not None and getattr(response, "generations", None):
            for gen_list in response.generations:
                for gen in gen_list:
                    text = getattr(gen, "text", "") or ""
                    if text:
                        b = text.encode("utf-8")
                        state.hasher.update(len(b).to_bytes(8, "big"))
                        state.hasher.update(b)

        transcript_sha256 = state.hasher.hexdigest()

        receipt_fields: Dict[str, Any] = {
            "schema_id": self.schema_id,
            "run_id": key,
            "timestamp_utc": self._utc_now(),
            "deployer_id": self.deployer_id,
            "transcript_sha256": transcript_sha256,
        }
        # Schema-specific defaults so the quickstart works without ceremony.
        if self.schema_id in ("chatbot_session/v1", "generated_content/v1"):
            receipt_fields.setdefault("model_identifier", state.model_identifier)
        if self.schema_id == "generated_content/v1":
            receipt_fields.setdefault("content_type", "text/plain")
        # Caller-supplied extras override defaults.
        receipt_fields.update(self.extra)

        # Validate against the Pydantic schema (raises if malformed / GDPR-unsafe).
        validated = get_schema(self.schema_id)(**receipt_fields).model_dump()

        # Canonical CBOR + Ed25519 signature over the SHA-256 digest of the body.
        body_bytes = canonical_encode(validated)
        body_digest = hashlib.sha256(body_bytes).digest()
        signature = self.signer.sign(body_digest)

        envelope: Dict[str, Any] = {
            "body": validated,
            "body_sha256": body_digest.hex(),
            "signature_ed25519": base64.urlsafe_b64encode(signature).rstrip(b"=").decode("ascii"),
            "public_key_ed25519": self.signer.public_key_b64(),
            "alg": "Ed25519",
        }

        self.emitter.emit(envelope)

    def on_llm_error(
        self,
        error: BaseException,
        *,
        run_id: Optional[uuid.UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Drop the run state on error. No receipt is emitted for failed runs."""
        key = self._run_key(run_id)
        with self._lock:
            self._runs.pop(key, None)
