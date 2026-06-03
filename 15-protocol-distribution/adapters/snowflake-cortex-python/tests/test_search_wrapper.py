"""Cortex Search Service wrapper tests."""

from tests.conftest import capture_sink, _FakeSession, _service_resolver_default


def test_search_emits_cortex_search_rag_receipt():
    from ledgerproof_snowflake_cortex import LedgerProofCortexSearch
    from ledgerproof_snowflake_cortex.canonical import canonical_decode

    sink, captured = capture_sink()
    search = LedgerProofCortexSearch(
        session=_FakeSession(),
        service_resolver=_service_resolver_default,
        lpr_deployer_id="d-test",
        lpr_sink=sink,
    )
    result = search.query(
        service_name="AI_APP.PUBLIC.SUPPORT_KB",
        query="How do I rotate the masking policy?",
        columns=["CHUNK", "SOURCE_URL"],
        limit=5,
        completion_text="Use ALTER MASKING POLICY ...",
        lpr_subject_id_hash="sha256:" + "c" * 64,
        lpr_disclosure_shown=True,
    )
    assert "results" in result
    search.flush()
    assert len(captured) == 1
    payload = canonical_decode(captured[0].payload_cbor)["payload"]
    assert payload["schema_name"] == "cortex_search_rag/v1"
    assert payload["search_service_name"] == "AI_APP.PUBLIC.SUPPORT_KB"
    assert payload["retrieved_doc_count"] == 3
    assert payload["retrieval_fingerprint_hash"].startswith("sha256:")
    assert payload["disclosure_shown"] is True
    assert payload["columns_returned"] == ["CHUNK", "SOURCE_URL"]


def test_search_skip_does_not_emit():
    from ledgerproof_snowflake_cortex import LedgerProofCortexSearch

    sink, captured = capture_sink()
    search = LedgerProofCortexSearch(
        session=_FakeSession(),
        service_resolver=_service_resolver_default,
        lpr_deployer_id="d-test",
        lpr_sink=sink,
    )
    search.query(
        service_name="AI_APP.PUBLIC.SUPPORT_KB",
        query="anything",
        lpr_skip=True,
    )
    search.flush()
    assert len(captured) == 0


def test_search_requires_session_or_resolver():
    import pytest
    from ledgerproof_snowflake_cortex import LedgerProofCortexSearch

    with pytest.raises(ValueError):
        LedgerProofCortexSearch(lpr_deployer_id="d-test")


def test_search_receipt_signature_locally_verifiable():
    from ledgerproof_snowflake_cortex import LedgerProofCortexSearch
    from ledgerproof_snowflake_cortex.signer import verify_signature

    sink, captured = capture_sink()
    search = LedgerProofCortexSearch(
        session=_FakeSession(),
        service_resolver=_service_resolver_default,
        lpr_deployer_id="d-test",
        lpr_sink=sink,
    )
    search.query(
        service_name="AI_APP.PUBLIC.SUPPORT_KB",
        query="anything",
    )
    search.flush()
    r = captured[0]
    assert verify_signature(r.public_key_b64, r.signature, r.payload_cbor)
