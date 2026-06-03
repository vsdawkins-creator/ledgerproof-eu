"""Manual emit_receipt tests, including citation extraction."""

import hashlib
import queue
from types import SimpleNamespace

from ledgerproof_perplexity import (
    QueueEmitter,
    citation_list_hash_hex,
    emit_receipt,
    extract_citations,
)


def _fake_response(
    text: str = "hi from sonar",
    model: str = "sonar",
    citations: list[str] | None = None,
):
    """Build an object shaped like a Perplexity ChatCompletion."""
    message = SimpleNamespace(role="assistant", content=text)
    choice = SimpleNamespace(index=0, message=message, finish_reason="stop")
    return SimpleNamespace(
        id="pplx-cmpl-99",
        model=model,
        choices=[choice],
        citations=citations or [],
    )


def test_extract_citations_from_direct_attribute():
    resp = _fake_response(citations=["https://a.example/1", "https://b.example/2"])
    cites = extract_citations(resp)
    assert cites == ["https://a.example/1", "https://b.example/2"]


def test_extract_citations_from_dict_shape():
    """Some SDK shapes hand back a plain dict."""
    raw = {"id": "x", "model": "sonar", "citations": ["https://c.example/3"]}
    assert extract_citations(raw) == ["https://c.example/3"]


def test_extract_citations_returns_empty_when_missing():
    resp = SimpleNamespace(id="x", model="sonar", choices=[])
    assert extract_citations(resp) == []


def test_manual_emit_basic_receipt():
    q: queue.Queue = queue.Queue()
    resp = _fake_response()
    env = emit_receipt(
        resp,
        deployer_id="urn:eu:deployer:acme",
        messages=[{"role": "user", "content": "hello"}],
        emitter=QueueEmitter(q),
    )
    assert env["receipt"]["model_id"] == "sonar"
    assert env["receipt"]["model_provider"] == "perplexity"
    assert env["adapter"]["name"] == "ledgerproof-perplexity"
    assert q.get_nowait() == env


def test_manual_emit_auto_extracts_citations_for_ai_search_schema():
    q: queue.Queue = queue.Queue()
    urls = ["https://a.example/1", "https://b.example/2", "https://c.example/3"]
    resp = _fake_response(text="See sources.", citations=urls)
    env = emit_receipt(
        resp,
        deployer_id="urn:eu:deployer:acme",
        messages=[{"role": "user", "content": "research?"}],
        regulatory_context={"schema": "ai_search_with_citations/v1"},
        emitter=QueueEmitter(q),
    )
    assert env["receipt"]["schema_id"] == "ai_search_with_citations/v1"
    assert env["receipt"]["citations_count"] == 3
    assert env["receipt"]["citations_sha256"] == citation_list_hash_hex(urls)


def test_manual_emit_public_interest_text_with_disclosure_and_review():
    q: queue.Queue = queue.Queue()
    urls = ["https://news.example/article/42"]
    resp = _fake_response(text="Breaking summary.", citations=urls)
    env = emit_receipt(
        resp,
        deployer_id="urn:eu:deployer:acme-media-de",
        messages=[{"role": "user", "content": "summarise"}],
        regulatory_context={"schema": "public_interest_text/v1"},
        extra_fields={
            "disclosure_label_shown": True,
            "editorial_review": True,
            "subject_category": "news.civic",
        },
        emitter=QueueEmitter(q),
    )
    assert env["receipt"]["schema_id"] == "public_interest_text/v1"
    assert env["receipt"]["article_basis"] == "EU_AI_Act_Art_50_4"
    assert env["receipt"]["disclosure_label_shown"] is True
    assert env["receipt"]["editorial_review"] is True
    assert env["receipt"]["subject_category"] == "news.civic"
    # Auto-extracted from response.citations
    assert env["receipt"]["citations_sha256"] == citation_list_hash_hex(urls)
    assert env["receipt"]["citations_count"] == 1


def test_manual_emit_respects_caller_provided_citations_hash():
    """If the deployer overrides the citation hash, do not stomp it."""
    q: queue.Queue = queue.Queue()
    resp = _fake_response(citations=["https://will.be.ignored.example"])
    custom_hash = hashlib.sha256(b"deployer-canonical-form").hexdigest()
    env = emit_receipt(
        resp,
        deployer_id="urn:eu:deployer:acme",
        messages=[{"role": "user", "content": "x"}],
        regulatory_context={"schema": "ai_search_with_citations/v1"},
        extra_fields={"citations_sha256": custom_hash, "citations_count": 7},
        emitter=QueueEmitter(q),
    )
    assert env["receipt"]["citations_sha256"] == custom_hash
    assert env["receipt"]["citations_count"] == 7
