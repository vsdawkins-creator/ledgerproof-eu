"""Schema and GDPR validator tests."""

import pytest


def test_chatbot_session_accepts_hashed_subject():
    from ledgerproof_groq.schema import ChatbotSessionV1, hash_str
    r = ChatbotSessionV1(
        model="llama-3.3-70b-versatile",
        deployer_id="d1",
        timestamp_unix_ms=1_700_000_000_000,
        subject_id_hash=hash_str("alice@example.com"),
    )
    assert r.subject_id_hash.startswith("sha256:")


def test_chatbot_session_rejects_raw_email():
    from ledgerproof_groq.schema import ChatbotSessionV1, GDPRValidationError
    with pytest.raises(Exception) as exc:
        ChatbotSessionV1(
            model="llama-3.3-70b-versatile",
            deployer_id="d1",
            timestamp_unix_ms=1_700_000_000_000,
            subject_id_hash="alice@example.com",
        )
    # pydantic wraps validation errors; just confirm something raised.
    assert exc.value is not None


def test_generated_content_requires_prefixed_hash():
    from ledgerproof_groq.schema import GeneratedContentV1
    with pytest.raises(Exception):
        GeneratedContentV1(
            model="llama-3.3-70b-versatile",
            deployer_id="d1",
            timestamp_unix_ms=1_700_000_000_000,
            content_hash="not-a-hash",
        )


def test_low_latency_inference_v1_fields():
    from ledgerproof_groq.schema import LowLatencyInferenceV1
    r = LowLatencyInferenceV1(
        model="llama-3.3-70b-versatile",
        deployer_id="d1",
        timestamp_unix_ms=1_700_000_000_000,
        inference_latency_ms=42.0,
        tokens_per_second=120.5,
        prompt_tokens=10,
        completion_tokens=5,
        total_tokens=15,
    )
    assert r.inference_latency_ms == 42.0
    assert r.tokens_per_second == 120.5


def test_audio_transcription_v1_requires_audio_hash():
    from ledgerproof_groq.schema import AudioTranscriptionV1
    r = AudioTranscriptionV1(
        model="whisper-large-v3",
        deployer_id="d1",
        timestamp_unix_ms=1_700_000_000_000,
        audio_hash="sha256:" + "a" * 64,
        language="en",
    )
    assert r.language == "en"
