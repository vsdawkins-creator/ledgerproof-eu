"""Tests for the GDPR safety net."""

from __future__ import annotations

import pytest

from ledgerproof.errors import GDPRSafetyError
from ledgerproof.gdpr import (
    assert_legal_entity_id,
    assert_no_pii,
    contains_pii,
)


class TestContainsPii:
    @pytest.mark.parametrize(
        "value,expected",
        [
            ("normal text without PII", None),
            ("LEI:5493001KJTIIGC8Y1R12", None),
            ("Acme Corp", None),
            ("user@example.com", "email address"),
            ("contact us at hello@example.org thanks", "email address"),
            ("DE89370400440532013000", "IBAN"),
            ("123-45-6789", "US social security number"),
            ("123456789", "US social security number"),  # 9 digits w/o dashes
            ("+1 555 123 4567", "phone number"),
        ],
    )
    def test_detection(self, value: str, expected: str | None) -> None:
        assert contains_pii(value) == expected


class TestAssertNoPii:
    def test_passes_clean_string(self) -> None:
        # Should not raise.
        assert_no_pii("Acme Insurance AG", field_name="deployer_name")

    def test_rejects_email(self) -> None:
        with pytest.raises(GDPRSafetyError, match="email"):
            assert_no_pii("contact@acme.com", field_name="deployer_name")

    def test_error_includes_field_name(self) -> None:
        try:
            assert_no_pii("foo@bar.com", field_name="deployer_id")
        except GDPRSafetyError as exc:
            assert "deployer_id" in str(exc)


class TestAssertLegalEntityId:
    def test_accepts_lei(self) -> None:
        assert_legal_entity_id("LEI:5493001KJTIIGC8Y1R12")

    def test_accepts_euid(self) -> None:
        assert_legal_entity_id("EUID:DE:HRB123456")

    def test_accepts_vat(self) -> None:
        assert_legal_entity_id("VAT:DE123456789")

    def test_accepts_did(self) -> None:
        assert_legal_entity_id("did:web:example.com")

    def test_rejects_email(self) -> None:
        with pytest.raises(GDPRSafetyError):
            assert_legal_entity_id("personal@example.com")

    def test_rejects_empty(self) -> None:
        with pytest.raises(GDPRSafetyError):
            assert_legal_entity_id("")
