import pytest

from gtm.brand import BrandVoiceError, reject_pii_in_field, validate_copy


def test_validate_copy_accepts_clean() -> None:
    validate_copy("This is a plain, direct paragraph with no forbidden phrases.")


def test_validate_copy_rejects_hope_youre_well() -> None:
    with pytest.raises(BrandVoiceError):
        validate_copy("Hi there — hope you're well.")


def test_validate_copy_rejects_synergy() -> None:
    with pytest.raises(BrandVoiceError):
        validate_copy("This represents a powerful synergy between the teams.")


def test_validate_copy_rejects_we_believe() -> None:
    with pytest.raises(BrandVoiceError):
        validate_copy("We believe AI compliance is the next big thing.")


def test_reject_pii_in_deployer_id() -> None:
    with pytest.raises(BrandVoiceError):
        reject_pii_in_field("deployer_id", "alice@example.com")


def test_reject_pii_in_review_rationale() -> None:
    with pytest.raises(BrandVoiceError):
        reject_pii_in_field("review_rationale", "Approved by bob@firm.com")


def test_reject_pii_allows_non_email_in_protected_field() -> None:
    reject_pii_in_field("deployer_id", "did:web:example.com")


def test_reject_pii_allows_email_outside_protected_fields() -> None:
    # We only reject in policy-protected fields.
    reject_pii_in_field("contact_email", "veronica@ledgerproofhq.io")
