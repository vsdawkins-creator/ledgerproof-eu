"""Cortex wrapper tests using the fake `snowflake.cortex` surface."""

from tests.conftest import capture_sink, _FakeSession


def test_complete_emits_chatbot_session_receipt_by_default():
    from ledgerproof_snowflake_cortex import LedgerProofCortex
    from ledgerproof_snowflake_cortex.canonical import canonical_decode

    sink, captured = capture_sink()
    client = LedgerProofCortex(
        session=_FakeSession(),
        lpr_deployer_id="d-test",
        lpr_sink=sink,
    )
    out = client.complete("llama3.1-70b", "Hello?")
    assert isinstance(out, str)
    client.flush()
    assert len(captured) == 1
    payload = canonical_decode(captured[0].payload_cbor)["payload"]
    assert payload["schema_name"] == "chatbot_session/v1"
    assert payload["model"] == "llama3.1-70b"
    assert payload["completion_hash"].startswith("sha256:")


def test_complete_with_chat_messages_list():
    from ledgerproof_snowflake_cortex import LedgerProofCortex
    sink, captured = capture_sink()
    client = LedgerProofCortex(
        session=_FakeSession(),
        lpr_deployer_id="d-test",
        lpr_sink=sink,
    )
    out = client.complete(
        "claude-3-5-sonnet",
        [
            {"role": "user", "content": "What is Snowflake Cortex?"},
            {"role": "assistant", "content": "An in-warehouse LLM surface."},
            {"role": "user", "content": "Tell me more."},
        ],
        lpr_subject_id_hash="sha256:" + "a" * 64,
    )
    assert isinstance(out, str)
    client.flush()
    assert len(captured) == 1


def test_complete_enterprise_data_lineage_schema():
    from ledgerproof_snowflake_cortex import LedgerProofCortex
    from ledgerproof_snowflake_cortex.canonical import canonical_decode

    sink, captured = capture_sink()
    client = LedgerProofCortex(
        session=_FakeSession(),
        lpr_deployer_id="d-test",
        lpr_sink=sink,
    )
    client.complete(
        "claude-3-5-sonnet",
        "Summarise the Q3 risk register.",
        lpr_schema="enterprise_data_lineage/v1",
        lpr_warehouse="COMPUTE_WH",
        lpr_source_database="CRM_PROD",
        lpr_source_schema="ACCOUNTS",
        lpr_source_tables=["CUSTOMER_360", "INTERACTION_LOG"],
        lpr_query_id="01abcd-0000-0001",
        lpr_role="AI_APP_RW",
    )
    client.flush()
    payload = canonical_decode(captured[0].payload_cbor)["payload"]
    assert payload["schema_name"] == "enterprise_data_lineage/v1"
    assert payload["warehouse"] == "COMPUTE_WH"
    assert payload["source_database"] == "CRM_PROD"
    assert payload["source_tables"] == ["CUSTOMER_360", "INTERACTION_LOG"]
    assert payload["query_id"] == "01abcd-0000-0001"


def test_complete_generated_content_explicit():
    from ledgerproof_snowflake_cortex import LedgerProofCortex
    from ledgerproof_snowflake_cortex.canonical import canonical_decode

    sink, captured = capture_sink()
    client = LedgerProofCortex(
        session=_FakeSession(),
        lpr_deployer_id="d-test",
        lpr_sink=sink,
    )
    client.complete(
        "mistral-large",
        "Generate marketing copy.",
        lpr_schema="generated_content/v1",
        lpr_marking_method="visible-label",
    )
    client.flush()
    payload = canonical_decode(captured[0].payload_cbor)["payload"]
    assert payload["schema_name"] == "generated_content/v1"
    assert payload["marking_method"] == "visible-label"


def test_summarize_emits_generated_content():
    from ledgerproof_snowflake_cortex import LedgerProofCortex
    from ledgerproof_snowflake_cortex.canonical import canonical_decode

    sink, captured = capture_sink()
    client = LedgerProofCortex(
        session=_FakeSession(),
        lpr_deployer_id="d-test",
        lpr_sink=sink,
    )
    out = client.summarize("Long body of text to summarise...")
    assert isinstance(out, str)
    client.flush()
    payload = canonical_decode(captured[0].payload_cbor)["payload"]
    assert payload["schema_name"] == "generated_content/v1"


def test_translate_emits_receipt():
    from ledgerproof_snowflake_cortex import LedgerProofCortex
    sink, captured = capture_sink()
    client = LedgerProofCortex(
        session=_FakeSession(),
        lpr_deployer_id="d-test",
        lpr_sink=sink,
    )
    out = client.translate("Hello, world", "en", "fr")
    assert "[fr]" in out
    client.flush()
    assert len(captured) == 1


def test_extract_answer_emits_receipt():
    from ledgerproof_snowflake_cortex import LedgerProofCortex
    sink, captured = capture_sink()
    client = LedgerProofCortex(
        session=_FakeSession(),
        lpr_deployer_id="d-test",
        lpr_sink=sink,
    )
    out = client.extract_answer("Doc body.", "What is the answer?")
    assert isinstance(out, list)
    client.flush()
    assert len(captured) == 1


def test_sentiment_emits_receipt():
    from ledgerproof_snowflake_cortex import LedgerProofCortex
    sink, captured = capture_sink()
    client = LedgerProofCortex(
        session=_FakeSession(),
        lpr_deployer_id="d-test",
        lpr_sink=sink,
    )
    score = client.sentiment("Great service.")
    assert isinstance(score, float)
    client.flush()
    assert len(captured) == 1


def test_lpr_skip_does_not_emit():
    from ledgerproof_snowflake_cortex import LedgerProofCortex
    sink, captured = capture_sink()
    client = LedgerProofCortex(
        session=_FakeSession(),
        lpr_deployer_id="d-test",
        lpr_sink=sink,
    )
    client.complete("llama3.1-70b", "Hi", lpr_skip=True)
    client.flush()
    assert len(captured) == 0


def test_receipt_signature_locally_verifiable():
    from ledgerproof_snowflake_cortex import LedgerProofCortex
    from ledgerproof_snowflake_cortex.signer import verify_signature

    sink, captured = capture_sink()
    client = LedgerProofCortex(
        session=_FakeSession(),
        lpr_deployer_id="d-test",
        lpr_sink=sink,
    )
    client.complete("llama3.1-70b", "Hi")
    client.flush()
    r = captured[0]
    assert verify_signature(r.public_key_b64, r.signature, r.payload_cbor)
