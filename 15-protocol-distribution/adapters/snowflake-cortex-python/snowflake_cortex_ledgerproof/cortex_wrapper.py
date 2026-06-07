"""Snowflake Cortex wrapper with LedgerProof side-channel receipts.

Wraps the public `snowflake.cortex` surface:

    Complete, Summarize, Translate, ExtractAnswer, Sentiment

The wrapper is a thin proxy. It never alters Cortex's request or response
(C7). It captures: model id (where applicable), prompt + completion hashes,
and — for the Snowflake-specific schemas — warehouse, database, schema, and
table-source attribution.

LedgerProof-specific kwargs are all prefixed `lpr_*` and are intercepted
before the call reaches `snowflake.cortex`.
"""

from __future__ import annotations

import hashlib
import os
import time
from typing import Any, Dict, Iterable, List, Optional, Union

from .emitter import AsyncEmitter, ReceiptSink, build_signed_receipt, default_sink_from_env
from .schema import (
    ChatbotSessionV1,
    EnterpriseDataLineageV1,
    GeneratedContentV1,
    ReceiptSchemaName,
)
from .signer import Ed25519Signer, load_signer_from_pem

_LPR_KWARGS = {
    "lpr_schema",
    "lpr_subject_id_hash",
    "lpr_session_id_hash",
    "lpr_prompt_hash",
    "lpr_disclosure_shown",
    "lpr_marking_method",
    "lpr_warehouse",
    "lpr_source_database",
    "lpr_source_schema",
    "lpr_source_tables",
    "lpr_query_id",
    "lpr_role",
    "lpr_skip",
}


def _sha256(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _pop_lpr(kwargs: dict) -> dict:
    return {k[4:]: kwargs.pop(k) for k in list(kwargs.keys()) if k in _LPR_KWARGS}


def _coerce_messages_to_text(messages_or_prompt: Any) -> str:
    """Flatten chat-style messages or a bare prompt into a single string."""
    if isinstance(messages_or_prompt, str):
        return messages_or_prompt
    if isinstance(messages_or_prompt, list):
        out: list[str] = []
        for m in messages_or_prompt:
            if isinstance(m, dict):
                c = m.get("content")
                if isinstance(c, str):
                    out.append(c)
                elif isinstance(c, list):
                    # Some chat APIs use content-parts lists.
                    for part in c:
                        if isinstance(part, dict):
                            t = part.get("text")
                            if isinstance(t, str):
                                out.append(t)
            elif isinstance(m, str):
                out.append(m)
        return "".join(out)
    return str(messages_or_prompt)


def _result_to_text(result: Any) -> str:
    """Normalise a Cortex result into a string for hashing.

    Cortex `Complete` returns either a `str` (single-prompt) or a structured
    object for chat completions. `Summarize`, `Translate`, `Sentiment` return
    primitives. `ExtractAnswer` returns a list-of-dict structure.
    """
    if result is None:
        return ""
    if isinstance(result, str):
        return result
    if isinstance(result, (int, float, bool)):
        return str(result)
    if isinstance(result, (list, tuple)):
        return "".join(_result_to_text(x) for x in result)
    # Try common dict shapes returned by Cortex.
    if isinstance(result, dict):
        for k in ("answer", "text", "translation", "summary", "completion", "content"):
            if k in result and isinstance(result[k], (str, int, float)):
                return str(result[k])
        return str(result)
    # Object with attributes — best-effort.
    for attr in ("text", "content", "completion"):
        v = getattr(result, attr, None)
        if isinstance(v, (str, int, float)):
            return str(v)
    return str(result)


class LedgerProofCortex:
    """LedgerProof-wrapped surface over `snowflake.cortex`.

    Construct with an authenticated `snowflake.snowpark.Session` and a
    signing key. The wrapper exposes one method per public Cortex function:

        .complete(model, prompt_or_messages, **lpr_kwargs)
        .summarize(text, **lpr_kwargs)
        .translate(text, from_language, to_language, **lpr_kwargs)
        .extract_answer(text, question, **lpr_kwargs)
        .sentiment(text, **lpr_kwargs)

    Each method emits a side-channel receipt after the underlying Cortex
    call returns, without altering or delaying the response.
    """

    def __init__(
        self,
        *,
        session: Any,
        lpr_signing_key_path: Optional[Union[str, os.PathLike]] = None,
        lpr_signer: Optional[Ed25519Signer] = None,
        lpr_deployer_id: str,
        lpr_sink: Optional[ReceiptSink] = None,
        lpr_emitter: Optional[AsyncEmitter] = None,
    ):
        if lpr_signer is None and lpr_signing_key_path is None:
            # Generate ephemeral key for dev/test. Production callers should
            # supply their own.
            lpr_signer = Ed25519Signer.generate()
        elif lpr_signer is None:
            lpr_signer = load_signer_from_pem(lpr_signing_key_path)  # type: ignore[arg-type]

        self._session = session
        self._signer = lpr_signer
        self._deployer_id = lpr_deployer_id
        self._emitter = lpr_emitter or AsyncEmitter(lpr_sink or default_sink_from_env())

        # Lazy-import the Cortex surface so the package remains importable
        # even when `snowflake.cortex` is shimmed for testing.
        from snowflake import cortex as _cortex  # type: ignore[import-not-found]
        self._cortex = _cortex

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def session(self) -> Any:
        return self._session

    @property
    def signer(self) -> Ed25519Signer:
        return self._signer

    def flush(self, timeout: float = 5.0) -> None:
        self._emitter.flush(timeout)

    def close(self) -> None:
        self._emitter.close()

    # ------------------------------------------------------------------
    # Cortex surfaces
    # ------------------------------------------------------------------

    def complete(
        self,
        model: str,
        prompt: Any,
        **kwargs: Any,
    ) -> Any:
        """Wrap `snowflake.cortex.Complete`.

        `prompt` may be a string or a chat-style messages list, matching the
        Cortex `Complete` signature.
        """
        lpr_opts = _pop_lpr(kwargs)
        if lpr_opts.get("skip"):
            return self._cortex.Complete(model, prompt, session=self._session, **kwargs)

        prompt_text = _coerce_messages_to_text(prompt)
        t0 = time.monotonic()
        result = self._cortex.Complete(model, prompt, session=self._session, **kwargs)
        latency_ms = (time.monotonic() - t0) * 1000

        # Cortex may return an iterator for the (rare) streamed path. Treat
        # any non-string, non-mapping iterable as a stream and wrap it.
        if (
            hasattr(result, "__iter__")
            and not isinstance(result, (str, bytes, dict, list, tuple))
        ):
            return self._wrap_stream(result, lpr_opts, model, prompt_text, t0)

        completion_text = _result_to_text(result)
        self._emit_inference_receipt(
            lpr_opts,
            model=model,
            prompt_text=prompt_text,
            completion_text=completion_text,
            latency_ms=latency_ms,
            default_schema=ReceiptSchemaName.CHATBOT_SESSION_V1,
        )
        return result

    def summarize(self, text: str, **kwargs: Any) -> Any:
        return self._simple_call(
            fn_name="Summarize",
            text=text,
            kwargs=kwargs,
            cortex_args=(text,),
            cortex_kwargs={},
            default_model="snowflake-cortex-summarize",
            default_schema=ReceiptSchemaName.GENERATED_CONTENT_V1,
        )

    def translate(
        self,
        text: str,
        from_language: str,
        to_language: str,
        **kwargs: Any,
    ) -> Any:
        return self._simple_call(
            fn_name="Translate",
            text=text,
            kwargs=kwargs,
            cortex_args=(text, from_language, to_language),
            cortex_kwargs={},
            default_model="snowflake-cortex-translate",
            default_schema=ReceiptSchemaName.GENERATED_CONTENT_V1,
        )

    def extract_answer(self, text: str, question: str, **kwargs: Any) -> Any:
        return self._simple_call(
            fn_name="ExtractAnswer",
            text=text + "\n\n" + question,
            kwargs=kwargs,
            cortex_args=(text, question),
            cortex_kwargs={},
            default_model="snowflake-cortex-extract-answer",
            default_schema=ReceiptSchemaName.GENERATED_CONTENT_V1,
        )

    def sentiment(self, text: str, **kwargs: Any) -> Any:
        return self._simple_call(
            fn_name="Sentiment",
            text=text,
            kwargs=kwargs,
            cortex_args=(text,),
            cortex_kwargs={},
            default_model="snowflake-cortex-sentiment",
            default_schema=ReceiptSchemaName.GENERATED_CONTENT_V1,
        )

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _simple_call(
        self,
        *,
        fn_name: str,
        text: str,
        kwargs: dict,
        cortex_args: tuple,
        cortex_kwargs: dict,
        default_model: str,
        default_schema: ReceiptSchemaName,
    ) -> Any:
        lpr_opts = _pop_lpr(kwargs)
        cortex_fn = getattr(self._cortex, fn_name)
        if lpr_opts.get("skip"):
            return cortex_fn(*cortex_args, session=self._session,
                             **cortex_kwargs, **kwargs)

        t0 = time.monotonic()
        result = cortex_fn(*cortex_args, session=self._session,
                           **cortex_kwargs, **kwargs)
        latency_ms = (time.monotonic() - t0) * 1000
        completion_text = _result_to_text(result)
        self._emit_inference_receipt(
            lpr_opts,
            model=default_model,
            prompt_text=text,
            completion_text=completion_text,
            latency_ms=latency_ms,
            default_schema=default_schema,
        )
        return result

    def _wrap_stream(
        self,
        stream: Iterable[Any],
        lpr_opts: dict,
        model: str,
        prompt_text: str,
        t0: float,
    ) -> Iterable[Any]:
        def gen():
            chunks: list[str] = []
            try:
                for ev in stream:
                    chunks.append(_result_to_text(ev))
                    yield ev
            finally:
                latency_ms = (time.monotonic() - t0) * 1000
                self._emit_inference_receipt(
                    lpr_opts,
                    model=model,
                    prompt_text=prompt_text,
                    completion_text="".join(chunks),
                    latency_ms=latency_ms,
                    default_schema=ReceiptSchemaName.CHATBOT_SESSION_V1,
                )
        return gen()

    def _emit_inference_receipt(
        self,
        lpr_opts: dict,
        *,
        model: str,
        prompt_text: str,
        completion_text: str,
        latency_ms: float,
        default_schema: ReceiptSchemaName,
    ) -> None:
        schema_name = lpr_opts.get("schema")
        if schema_name is None:
            schema_name = default_schema
        if isinstance(schema_name, str):
            schema_name = ReceiptSchemaName(schema_name)

        ts = int(time.time() * 1000)
        common: Dict[str, Any] = {
            "deployer_id": self._deployer_id,
            "model": model,
            "timestamp_unix_ms": ts,
        }

        if schema_name == ReceiptSchemaName.CHATBOT_SESSION_V1:
            receipt = ChatbotSessionV1(
                **common,
                subject_id_hash=lpr_opts.get("subject_id_hash"),
                session_id_hash=lpr_opts.get("session_id_hash"),
                prompt_hash=lpr_opts.get("prompt_hash") or _sha256(prompt_text),
                completion_hash=_sha256(completion_text),
                disclosure_shown=bool(lpr_opts.get("disclosure_shown", False)),
            )
        elif schema_name == ReceiptSchemaName.GENERATED_CONTENT_V1:
            receipt = GeneratedContentV1(
                **common,
                content_hash=_sha256(completion_text),
                content_type="text",
                marking_method=lpr_opts.get("marking_method"),
            )
        elif schema_name == ReceiptSchemaName.ENTERPRISE_DATA_LINEAGE_V1:
            tables = lpr_opts.get("source_tables") or []
            if isinstance(tables, str):
                tables = [tables]
            receipt = EnterpriseDataLineageV1(
                **common,
                content_hash=_sha256(completion_text),
                content_type="text",
                marking_method=lpr_opts.get("marking_method"),
                warehouse=lpr_opts.get("warehouse"),
                source_database=lpr_opts.get("source_database"),
                source_schema=lpr_opts.get("source_schema"),
                source_tables=list(tables),
                query_id=lpr_opts.get("query_id"),
                role=lpr_opts.get("role"),
            )
        else:
            # Fallback: treat as generic generated content.
            receipt = GeneratedContentV1(
                **common,
                content_hash=_sha256(completion_text),
            )

        self._emitter.submit(build_signed_receipt(receipt, self._signer))
