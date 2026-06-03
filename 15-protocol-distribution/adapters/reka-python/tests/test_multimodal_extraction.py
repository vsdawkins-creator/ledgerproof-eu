"""
Tests for the multimodal-message inspection helpers in client_wrapper.

These cover the GDPR-relevant edge cases: how raw bytes, data: URIs, and
URL-only references are turned into MediaRef entries WITHOUT phoning home (C4)
and WITHOUT storing raw text/media inside the receipt (GDPR data minimisation).
"""

from __future__ import annotations

import base64
import hashlib

from ledgerproof_reka.client_wrapper import (
    _extract_media_refs,
    _extract_user_message_text,
    _input_modalities,
    _select_schema,
)


def test_extract_text_from_string_content_block():
    messages = [{"role": "user", "content": "Plain string"}]
    assert _extract_user_message_text(messages) == "Plain string"


def test_extract_text_from_typed_content_blocks():
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "first"},
                {"type": "text", "text": "second"},
            ],
        }
    ]
    assert _extract_user_message_text(messages) == "first\nsecond"


def test_extract_media_ref_from_inline_base64_image():
    raw = b"\x89PNG\r\n\x1a\nfakepayload"
    b64 = base64.b64encode(raw).decode()
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": {"data": b64, "media_type": "image/png"}},
            ],
        }
    ]
    refs = _extract_media_refs(messages)
    assert len(refs) == 1
    assert refs[0].modality == "image"
    assert refs[0].mime_type == "image/png"
    assert refs[0].sha256_hex == hashlib.sha256(raw).hexdigest()
    assert refs[0].byte_length == len(raw)


def test_extract_media_ref_strips_data_uri_prefix():
    raw = b"audio-bytes"
    b64 = base64.b64encode(raw).decode()
    data_uri = f"data:audio/wav;base64,{b64}"
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "audio", "audio": {"data": data_uri}},
            ],
        }
    ]
    refs = _extract_media_refs(messages)
    assert len(refs) == 1
    assert refs[0].modality == "audio"
    assert refs[0].mime_type == "audio/wav"
    assert refs[0].sha256_hex == hashlib.sha256(raw).hexdigest()


def test_url_only_video_ref_is_hashed_by_uri_no_fetch():
    url = "https://cdn.example.com/clip.mp4"
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "video", "url": url, "media_type": "video/mp4"},
            ],
        }
    ]
    refs = _extract_media_refs(messages)
    assert len(refs) == 1
    ref = refs[0]
    assert ref.modality == "video"
    assert ref.mime_type == "video/mp4"
    # C4: hash equals sha256 of the URL bytes — the network was never touched.
    assert ref.source_uri_sha256_hex == hashlib.sha256(url.encode()).hexdigest()
    assert ref.descriptor == "uri-only"


def test_extract_media_refs_ignores_non_user_roles():
    messages = [
        {"role": "system", "content": [{"type": "image", "image": {"data": "AAAA"}}]},
        {"role": "user", "content": "just text"},
    ]
    assert _extract_media_refs(messages) == []


def test_select_schema_promotes_to_video_understanding_when_video_present():
    schema = _select_schema("chatbot_session/v1", ["text", "video"], tool_uses=[])
    assert schema == "video_understanding/v1"


def test_select_schema_promotes_to_multimodal_when_image_plus_text():
    schema = _select_schema("chatbot_session/v1", ["text", "image"], tool_uses=[])
    assert schema == "multimodal_native_inference/v1"


def test_select_schema_leaves_text_only_untouched():
    schema = _select_schema("chatbot_session/v1", ["text"], tool_uses=[])
    assert schema == "chatbot_session/v1"


def test_input_modalities_preserves_order_text_first():
    from ledgerproof_reka.schema import MediaRef

    media = [
        MediaRef(
            sha256_hex="a" * 64, byte_length=1, modality="image", mime_type="image/png"
        ),
        MediaRef(
            sha256_hex="b" * 64, byte_length=1, modality="video", mime_type="video/mp4"
        ),
    ]
    mods = _input_modalities(text_present=True, media=media)
    assert mods == ["text", "image", "video"]
