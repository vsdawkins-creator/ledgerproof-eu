"""Schema and GDPR validator tests."""

import pytest


def test_chatbot_session_accepts_hashed_subject():
    from ledgerproof_snowflake_cortex.schema import ChatbotSessionV1, hash_str
    r = ChatbotSessionV1(
        model="llama3.1-70b",
        deployer_id="d1",
        timestamp_unix_ms=1_700_000_000_000,
        subject_id_hash=hash_str("alice@example.com"),
    )
    assert r.subject_id_hash.startswith("sha256:")


def test_chatbot_session_rejects_raw_email():
    from ledgerproof_snowflake_cortex.schema import ChatbotSessionV1
    with pytest.raises(Exception):
        ChatbotSessionV1(
            model="llama3.1-70b",
            deployer_id="d1",
            timestamp_unix_ms=1_700_000_000_000,
            subject_id_hash="alice@example.com",
        )


def test_generated_content_requires_prefixed_hash():
    from ledgerproof_snowflake_cortex.schema import GeneratedContentV1
    with pytest.raises(Exception):
        GeneratedContentV1(
            model="llama3.1-70b",
            deployer_id="d1",
            timestamp_unix_ms=1_700_000_000_000,
            content_hash="not-a-hash",
        )


def test_enterprise_data_lineage_v1_full():
    from ledgerproof_snowflake_cortex.schema import EnterpriseDataLineageV1
    r = EnterpriseDataLineageV1(
        model="claude-3-5-sonnet",
        deployer_id="d1",
        timestamp_unix_ms=1_700_000_000_000,
        content_hash="sha256:" + "a" * 64,
        warehouse="COMPUTE_WH",
        source_database="CRM_PROD",
        source_schema="ACCOUNTS",
        source_tables=["CUSTOMER_360", "ACCOUNTS.INTERACTION_LOG"],
        query_id="01abcd-0000-0001",
        role="AI_APP_RW",
    )
    assert r.warehouse == "COMPUTE_WH"
    assert "CUSTOMER_360" in r.source_tables


def test_enterprise_data_lineage_rejects_bad_identifier():
    from ledgerproof_snowflake_cortex.schema import EnterpriseDataLineageV1
    with pytest.raises(Exception):
        EnterpriseDataLineageV1(
            model="claude-3-5-sonnet",
            deployer_id="d1",
            timestamp_unix_ms=1_700_000_000_000,
            content_hash="sha256:" + "a" * 64,
            warehouse="not a; legal identifier",
        )


def test_enterprise_data_lineage_rejects_bad_table():
    from ledgerproof_snowflake_cortex.schema import EnterpriseDataLineageV1
    with pytest.raises(Exception):
        EnterpriseDataLineageV1(
            model="claude-3-5-sonnet",
            deployer_id="d1",
            timestamp_unix_ms=1_700_000_000_000,
            content_hash="sha256:" + "a" * 64,
            source_tables=["DROP TABLE x"],
        )


def test_cortex_search_rag_v1_fields():
    from ledgerproof_snowflake_cortex.schema import CortexSearchRagV1
    r = CortexSearchRagV1(
        model="snowflake-cortex-search",
        deployer_id="d1",
        timestamp_unix_ms=1_700_000_000_000,
        search_service_name="AI_APP.PUBLIC.SUPPORT_KB",
        retrieved_doc_count=5,
        retrieval_fingerprint_hash="sha256:" + "b" * 64,
        columns_returned=["CHUNK", "SOURCE_URL"],
        disclosure_shown=True,
    )
    assert r.retrieved_doc_count == 5
    assert r.disclosure_shown is True


def test_cortex_search_rag_v1_rejects_bad_service_name():
    from ledgerproof_snowflake_cortex.schema import CortexSearchRagV1
    with pytest.raises(Exception):
        CortexSearchRagV1(
            model="snowflake-cortex-search",
            deployer_id="d1",
            timestamp_unix_ms=1_700_000_000_000,
            search_service_name="bad name; with semicolons",
        )


def test_cortex_search_rag_gdpr_on_query_hash():
    from ledgerproof_snowflake_cortex.schema import CortexSearchRagV1
    with pytest.raises(Exception):
        CortexSearchRagV1(
            model="snowflake-cortex-search",
            deployer_id="d1",
            timestamp_unix_ms=1_700_000_000_000,
            search_service_name="AI_APP.PUBLIC.SUPPORT_KB",
            query_hash="alice@example.com",
        )


def test_resolve_schema_by_string():
    from ledgerproof_snowflake_cortex.schema import (
        resolve_schema, EnterpriseDataLineageV1, CortexSearchRagV1,
    )
    assert resolve_schema("enterprise_data_lineage/v1") is EnterpriseDataLineageV1
    assert resolve_schema("cortex_search_rag/v1") is CortexSearchRagV1
