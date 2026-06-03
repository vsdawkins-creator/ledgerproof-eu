"""Schema and GDPR validator tests."""

import pytest


def test_chatbot_session_accepts_hashed_subject():
    from ledgerproof_cerebras.schema import ChatbotSessionV1, hash_str
    r = ChatbotSessionV1(
        model="llama3.1-70b",
        deployer_id="d1",
        timestamp_unix_ms=1_700_000_000_000,
        subject_id_hash=hash_str("alice@example.com"),
    )
    assert r.subject_id_hash.startswith("sha256:")


def test_chatbot_session_rejects_raw_email():
    from ledgerproof_cerebras.schema import ChatbotSessionV1
    with pytest.raises(Exception) as exc:
        ChatbotSessionV1(
            model="llama3.1-70b",
            deployer_id="d1",
            timestamp_unix_ms=1_700_000_000_000,
            subject_id_hash="alice@example.com",
        )
    assert exc.value is not None


def test_generated_content_requires_prefixed_hash():
    from ledgerproof_cerebras.schema import GeneratedContentV1
    with pytest.raises(Exception):
        GeneratedContentV1(
            model="llama3.1-70b",
            deployer_id="d1",
            timestamp_unix_ms=1_700_000_000_000,
            content_hash="not-a-hash",
        )


def test_wafer_scale_inference_v1_fields():
    from ledgerproof_cerebras.schema import WaferScaleInferenceV1
    r = WaferScaleInferenceV1(
        model="llama3.1-70b",
        deployer_id="d1",
        timestamp_unix_ms=1_700_000_000_000,
        inference_latency_ms=42.0,
        tokens_per_second=2200.0,
        prompt_tokens=10,
        completion_tokens=5,
        total_tokens=15,
    )
    assert r.inference_latency_ms == 42.0
    assert r.tokens_per_second == 2200.0
    assert r.hardware_class == "wafer-scale"


def test_wafer_scale_rejects_negative_latency():
    from ledgerproof_cerebras.schema import WaferScaleInferenceV1
    with pytest.raises(Exception):
        WaferScaleInferenceV1(
            model="llama3.1-70b",
            deployer_id="d1",
            timestamp_unix_ms=1_700_000_000_000,
            inference_latency_ms=-1.0,
        )


def test_reasoning_distilled_v1_fields():
    from ledgerproof_cerebras.schema import ReasoningDistilledV1
    r = ReasoningDistilledV1(
        model="deepseek-r1-distill-llama-70b",
        deployer_id="d1",
        timestamp_unix_ms=1_700_000_000_000,
        reasoning_tokens=120,
        completion_tokens=20,
        prompt_tokens=10,
        total_tokens=150,
        inference_latency_ms=80.5,
    )
    assert r.reasoning_tokens == 120
    assert r.completion_tokens == 20


def test_reasoning_distilled_gdpr_on_trace_hash():
    from ledgerproof_cerebras.schema import ReasoningDistilledV1
    with pytest.raises(Exception):
        ReasoningDistilledV1(
            model="deepseek-r1-distill-llama-70b",
            deployer_id="d1",
            timestamp_unix_ms=1_700_000_000_000,
            reasoning_trace_hash="bob@example.com",
        )


def test_resolve_schema_by_string():
    from ledgerproof_cerebras.schema import (
        resolve_schema, WaferScaleInferenceV1, ReasoningDistilledV1,
    )
    assert resolve_schema("wafer_scale_inference/v1") is WaferScaleInferenceV1
    assert resolve_schema("reasoning_distilled/v1") is ReasoningDistilledV1
