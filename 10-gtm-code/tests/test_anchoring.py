import pytest

from gtm.anchoring import MockBackend, default_backend


def test_mock_backend_issues_deterministic_receipt() -> None:
    b = MockBackend()
    h1 = b.issue(
        artifact_slug="t",
        body="hello",
        article50_subclause=None,
        profile="lpr.v1.2.baseline",
    )
    h2 = b.issue(
        artifact_slug="t",
        body="hello",
        article50_subclause=None,
        profile="lpr.v1.2.baseline",
    )
    assert h1.receipt_id == h2.receipt_id
    assert h1.is_mock


def test_mock_backend_different_body_produces_different_receipt() -> None:
    b = MockBackend()
    h1 = b.issue(artifact_slug="t", body="a", article50_subclause=None, profile="p")
    h2 = b.issue(artifact_slug="t", body="b", article50_subclause=None, profile="p")
    assert h1.receipt_id != h2.receipt_id


def test_default_backend_returns_mock_when_no_api_key() -> None:
    backend = default_backend()
    assert isinstance(backend, MockBackend)


def test_mock_backend_refuses_prod_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LPR_ENV", "prod")
    with pytest.raises(RuntimeError, match="MockBackend refuses"):
        MockBackend()
