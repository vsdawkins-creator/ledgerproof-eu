"""Decorator and manual emission tests."""

from tests.conftest import capture_sink


def test_lpr_track_decorator_sync():
    from ledgerproof_snowflake_cortex import lpr_track
    from ledgerproof_snowflake_cortex.emitter import AsyncEmitter
    from ledgerproof_snowflake_cortex.signer import Ed25519Signer

    sink, captured = capture_sink()
    emitter = AsyncEmitter(sink)
    signer = Ed25519Signer.generate()

    @lpr_track(signer=signer, deployer_id="d-deco", model="llama3.1-70b",
               emitter=emitter)
    def gen_text():
        return "synthetic text"

    out = gen_text()
    assert out == "synthetic text"
    emitter.flush()
    assert len(captured) == 1


def test_lpr_track_decorator_stream_aware():
    from ledgerproof_snowflake_cortex import lpr_track
    from ledgerproof_snowflake_cortex.emitter import AsyncEmitter
    from ledgerproof_snowflake_cortex.signer import Ed25519Signer

    sink, captured = capture_sink()
    emitter = AsyncEmitter(sink)
    signer = Ed25519Signer.generate()

    @lpr_track(signer=signer, deployer_id="d-deco", model="llama3.1-70b",
               emitter=emitter)
    def streamy():
        for piece in ["a", "b", "c"]:
            yield piece

    pieces = list(streamy())
    assert pieces == ["a", "b", "c"]
    emitter.flush()
    assert len(captured) == 1


def test_lpr_track_decorator_enterprise_data_lineage():
    from ledgerproof_snowflake_cortex import lpr_track
    from ledgerproof_snowflake_cortex.canonical import canonical_decode
    from ledgerproof_snowflake_cortex.emitter import AsyncEmitter
    from ledgerproof_snowflake_cortex.signer import Ed25519Signer

    sink, captured = capture_sink()
    emitter = AsyncEmitter(sink)
    signer = Ed25519Signer.generate()

    @lpr_track(
        signer=signer,
        deployer_id="d-deco",
        model="claude-3-5-sonnet",
        schema="enterprise_data_lineage/v1",
        emitter=emitter,
        extra_fields={
            "warehouse": "COMPUTE_WH",
            "source_database": "CRM_PROD",
            "source_schema": "ACCOUNTS",
            "source_tables": ["CUSTOMER_360"],
        },
    )
    def gen():
        return "Account summary."

    gen()
    emitter.flush()
    payload = canonical_decode(captured[0].payload_cbor)["payload"]
    assert payload["schema_name"] == "enterprise_data_lineage/v1"
    assert payload["warehouse"] == "COMPUTE_WH"
    assert payload["source_tables"] == ["CUSTOMER_360"]


def test_manual_emit_receipt_enterprise_data_lineage():
    from ledgerproof_snowflake_cortex import emit_receipt
    from ledgerproof_snowflake_cortex.emitter import AsyncEmitter
    from ledgerproof_snowflake_cortex.signer import Ed25519Signer

    sink, captured = capture_sink()
    emitter = AsyncEmitter(sink)
    signer = Ed25519Signer.generate()

    emit_receipt(
        "enterprise_data_lineage/v1",
        signer=signer,
        deployer_id="d-manual",
        model="claude-3-5-sonnet",
        emitter=emitter,
        fields={
            "content_hash": "sha256:" + "f" * 64,
            "warehouse": "COMPUTE_WH",
            "source_database": "CRM_PROD",
            "source_schema": "ACCOUNTS",
            "source_tables": ["CUSTOMER_360", "INTERACTION_LOG"],
        },
    )
    emitter.flush()
    assert len(captured) == 1


def test_manual_emit_receipt_cortex_search_rag():
    from ledgerproof_snowflake_cortex import emit_receipt
    from ledgerproof_snowflake_cortex.emitter import AsyncEmitter
    from ledgerproof_snowflake_cortex.signer import Ed25519Signer

    sink, captured = capture_sink()
    emitter = AsyncEmitter(sink)
    signer = Ed25519Signer.generate()

    emit_receipt(
        "cortex_search_rag/v1",
        signer=signer,
        deployer_id="d-manual",
        model="snowflake-cortex-search",
        emitter=emitter,
        fields={
            "search_service_name": "AI_APP.PUBLIC.SUPPORT_KB",
            "retrieved_doc_count": 5,
            "retrieval_fingerprint_hash": "sha256:" + "e" * 64,
            "columns_returned": ["CHUNK", "SOURCE_URL"],
            "disclosure_shown": True,
        },
    )
    emitter.flush()
    assert len(captured) == 1
