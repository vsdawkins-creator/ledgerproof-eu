"""GDPR safety net — prevent personal data from being transmitted to LedgerProof.

LPR receipts are designed so that personal data never enters the chain. The
server enforces this with schema-level validation (e.g., ``deployer_id`` MUST
NOT contain ``@``). This module enforces the same rules at the SDK boundary,
so users get a clear error *before* a network call rather than a server 400.

The architecture forbids the failures, not the policy. If you find yourself
wanting to bypass this module: stop. The right answer is to use legal-entity
identifiers (LEI, EUID, VAT, DID) for deployers and role identifiers
("senior-editor", not "Jane Doe") for human reviewers — never personal data.

See ``12-eu-compliance/03-GDPR-ARCHITECTURE-AND-DPA.md`` for the architectural
rationale, and ``12-eu-compliance/11-EU-ART50-GAP-ANALYSIS.md`` Gold-Standard
Angle #4 for why this is a competitive moat, not just a constraint.
"""

from __future__ import annotations

import re
from typing import Final

from .errors import GDPRSafetyError

# Conservative patterns. These reject obvious PII; they are not a full data-
# loss-prevention solution. The SDK relies on the deployer to not actively
# work around these checks.

_EMAIL_PATTERN: Final = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")

# IBANs: 2 letters + 2 digits + up to 30 alphanumerics. Match common formats.
_IBAN_PATTERN: Final = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{10,30}\b")

# US SSN: 3-2-4 digit groups (with or without dashes). Heuristic only.
_SSN_PATTERN: Final = re.compile(r"\b\d{3}-?\d{2}-?\d{4}\b")

# Phone numbers (E.164-ish). Heuristic; intentionally narrow to avoid false
# positives on dates/IDs.
_PHONE_PATTERN: Final = re.compile(r"\+\d{1,3}[\s-]?\d{2,4}[\s-]?\d{3,4}[\s-]?\d{3,4}")


def contains_pii(value: str) -> str | None:
    """Return a description of the first PII pattern found in ``value``, or None.

    Pure function, no side effects, no network. Use this if you want to
    check a string without raising — e.g., to log a warning instead of
    refusing.

    :param value: Any string the SDK is about to transmit.
    :returns: A short description like ``"email address"`` if PII is
        detected, otherwise ``None``.
    """
    if _EMAIL_PATTERN.search(value):
        return "email address"
    if _IBAN_PATTERN.search(value):
        return "IBAN"
    if _SSN_PATTERN.search(value):
        return "US social security number"
    if _PHONE_PATTERN.search(value):
        return "phone number"
    return None


def assert_no_pii(value: str, *, field_name: str) -> None:
    """Raise :class:`GDPRSafetyError` if ``value`` looks like personal data.

    Called by the SDK at the boundary of every public method that accepts
    free-text input destined for LedgerProof. Field names are passed through
    to the error message so the developer knows which field tripped the
    check.

    :param value: The string to check.
    :param field_name: The name of the field, for error messages
        (e.g., ``"deployer_id"``, ``"reviewer_role"``).
    :raises GDPRSafetyError: If a PII pattern matches.
    """
    finding = contains_pii(value)
    if finding is None:
        return
    raise GDPRSafetyError(
        f"Refusing to transmit {field_name}: detected what appears to be a "
        f"{finding}. LedgerProof receipts must not contain personal data. "
        f"Use a legal-entity identifier (LEI/EUID/VAT/DID) for deployers and "
        f"a role identifier (e.g., 'senior-editor') for human reviewers. "
        f"See https://docs.ledgerproofhq.io/explain/gdpr-and-lpr",
        context={"field": field_name, "detected": finding},
    )


def assert_legal_entity_id(value: str, *, field_name: str = "deployer_id") -> None:
    """Validate that ``value`` looks like a legal-entity identifier.

    Accepted prefixes (case-sensitive, per the LPR specification):

    - ``LEI:`` — Legal Entity Identifier (ISO 17442)
    - ``EUID:`` — European Unique Identifier
    - ``VAT:`` — Value Added Tax registration number
    - ``DID:`` — Decentralized Identifier (W3C)

    This is the same check the server applies. Catching it at the SDK
    boundary saves a network round-trip on misconfiguration.

    :param value: The candidate identifier.
    :param field_name: For error messages.
    :raises GDPRSafetyError: If the value contains ``@`` (looks like an
        email) or is empty.
    :raises ValueError: If the prefix is unrecognized. (Note: this is a
        ConfigurationError, not a GDPR one; the user picked the wrong
        format, not transmitted PII.)
    """
    if "@" in value:
        raise GDPRSafetyError(
            f"{field_name} must be a legal-entity identifier "
            f"(LEI/EUID/VAT/DID), not an email or personal identifier.",
            context={"field": field_name},
        )
    if not value:
        raise GDPRSafetyError(
            f"{field_name} must not be empty.",
            context={"field": field_name},
        )


__all__ = [
    "assert_legal_entity_id",
    "assert_no_pii",
    "contains_pii",
]
