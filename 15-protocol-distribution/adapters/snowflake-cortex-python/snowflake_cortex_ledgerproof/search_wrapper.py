"""Cortex Search Service wrapper with LedgerProof side-channel receipts.

Wraps the Cortex Search Service `.query()` surface accessible via the
Snowpark `Root` object:

    from snowflake.core import Root
    root = Root(session)
    svc = root.databases["AI_APP"].schemas["PUBLIC"].cortex_search_services["SUPPORT_KB"]
    svc.search(query=..., columns=[...], limit=...)

This wrapper emits a `cortex_search_rag/v1` receipt capturing the
fully-qualified search service name, the hashed retrieval fingerprint, and
the count of retrieved documents — never the row content.

Because the public Snowpark `Root` import surface has shifted between
`snowflake-snowpark-python` releases, the wrapper accepts an explicit
`search_service_callable` for callers who already hold a service handle.
"""

from __future__ import annotations

import hashlib
import os
import time
from typing import Any, Callable, List, Optional, Sequence, Union

from .emitter import AsyncEmitter, ReceiptSink, build_signed_receipt, default_sink_from_env
from .schema import CortexSearchRagV1, ReceiptSchemaName
from .signer import Ed25519Signer, load_signer_from_pem


_LPR_KWARGS = {
    "lpr_schema",
    "lpr_subject_id_hash",
    "lpr_session_id_hash",
    "lpr_query_hash",
    "lpr_disclosure_shown",
    "lpr_skip",
}


def _sha256(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _pop_lpr(kwargs: dict) -> dict:
    return {k[4:]: kwargs.pop(k) for k in list(kwargs.keys()) if k in _LPR_KWARGS}


def _extract_retrieved_docs(result: Any) -> tuple[int, List[str]]:
    """Best-effort extraction of (doc_count, fingerprint_inputs) from a
    Cortex Search Service result.

    Cortex returns a structure with a `results` list where each entry is a
    dict of column -> value. We hash the stringified rows, not the row
    content itself, so the fingerprint is stable but the receipt does not
    surface row data.
    """
    rows = None
    if result is None:
        return 0, []
    if isinstance(result, dict):
        rows = result.get("results") or result.get("matches") or result.get("hits")
    else:
        rows = getattr(result, "results", None)
        if rows is None:
            rows = getattr(result, "matches", None)
        if rows is None:
            rows = getattr(result, "hits", None)
    if rows is None and isinstance(result, list):
        rows = result
    if rows is None:
        return 0, []
    docs: List[str] = []
    for r in rows:
        if isinstance(r, dict):
            # Stable deterministic stringification of the row keys+values.
            items = sorted((str(k), str(v)) for k, v in r.items())
            docs.append("|".join(f"{k}={v}" for k, v in items))
        else:
            docs.append(str(r))
    return len(docs), docs


class LedgerProofCortexSearch:
    """LedgerProof-wrapped Cortex Search Service queries.

    Two construction modes:

    1. Pass a `session`; the wrapper will look up the service via
       `snowflake.core.Root(session)` (this requires `snowflake-snowpark-python`
       to have the `core` namespace available at runtime).
    2. Pass an explicit `service_resolver: Callable[[str], Any]` that maps a
       fully-qualified service name to a handle exposing `.search(...)`.
       This is the supported route when the runtime environment exposes
       the Cortex Search Service through a non-default import path.
    """

    def __init__(
        self,
        *,
        session: Optional[Any] = None,
        service_resolver: Optional[Callable[[str], Any]] = None,
        lpr_signing_key_path: Optional[Union[str, os.PathLike]] = None,
        lpr_signer: Optional[Ed25519Signer] = None,
        lpr_deployer_id: str,
        lpr_sink: Optional[ReceiptSink] = None,
        lpr_emitter: Optional[AsyncEmitter] = None,
    ):
        if session is None and service_resolver is None:
            raise ValueError(
                "LedgerProofCortexSearch requires either a Snowpark `session` "
                "or an explicit `service_resolver`."
            )

        if lpr_signer is None and lpr_signing_key_path is None:
            lpr_signer = Ed25519Signer.generate()
        elif lpr_signer is None:
            lpr_signer = load_signer_from_pem(lpr_signing_key_path)  # type: ignore[arg-type]

        self._session = session
        self._service_resolver = service_resolver
        self._signer = lpr_signer
        self._deployer_id = lpr_deployer_id
        self._emitter = lpr_emitter or AsyncEmitter(lpr_sink or default_sink_from_env())

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def signer(self) -> Ed25519Signer:
        return self._signer

    def flush(self, timeout: float = 5.0) -> None:
        self._emitter.flush(timeout)

    def close(self) -> None:
        self._emitter.close()

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def _resolve_service(self, service_name: str) -> Any:
        if self._service_resolver is not None:
            return self._service_resolver(service_name)
        # Best-effort default: import snowflake.core lazily.
        from snowflake.core import Root  # type: ignore[import-not-found]
        root = Root(self._session)
        parts = service_name.split(".")
        if len(parts) != 3:
            raise ValueError(
                "Default service_resolver requires a fully-qualified "
                "db.schema.service name."
            )
        db, schema, name = parts
        return (
            root.databases[db]
            .schemas[schema]
            .cortex_search_services[name]
        )

    def query(
        self,
        *,
        service_name: str,
        query: str,
        columns: Optional[Sequence[str]] = None,
        limit: int = 10,
        completion_text: Optional[str] = None,
        **kwargs: Any,
    ) -> Any:
        """Execute a Cortex Search Service query and emit a receipt.

        `completion_text` is the *final* answer string that will be shown
        to the natural person (the RAG output). If supplied, it is hashed
        into the receipt's `completion_hash` field. If omitted, only the
        retrieval fingerprint is recorded.
        """
        lpr_opts = _pop_lpr(kwargs)
        svc = self._resolve_service(service_name)

        # Prefer `.search(...)`; some surfaces also expose `.query(...)`.
        if hasattr(svc, "search"):
            search_fn = svc.search
        elif hasattr(svc, "query"):
            search_fn = svc.query
        else:
            raise AttributeError(
                "Cortex Search Service handle exposes neither .search nor .query."
            )

        t0 = time.monotonic()
        result = search_fn(
            query=query,
            columns=list(columns) if columns else None,
            limit=limit,
            **kwargs,
        )
        _latency_ms = (time.monotonic() - t0) * 1000  # noqa: F841 — reserved for future use

        if lpr_opts.get("skip"):
            return result

        doc_count, docs = _extract_retrieved_docs(result)
        fingerprint = _sha256("\n".join(docs)) if docs else None

        receipt = CortexSearchRagV1(
            deployer_id=self._deployer_id,
            model="snowflake-cortex-search",
            timestamp_unix_ms=int(time.time() * 1000),
            subject_id_hash=lpr_opts.get("subject_id_hash"),
            session_id_hash=lpr_opts.get("session_id_hash"),
            query_hash=lpr_opts.get("query_hash") or _sha256(query),
            completion_hash=_sha256(completion_text) if completion_text else None,
            disclosure_shown=bool(lpr_opts.get("disclosure_shown", False)),
            search_service_name=service_name,
            retrieved_doc_count=doc_count,
            retrieval_fingerprint_hash=fingerprint,
            columns_returned=list(columns) if columns else [],
        )
        self._emitter.submit(build_signed_receipt(receipt, self._signer))
        return result
