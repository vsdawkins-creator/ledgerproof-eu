"""Brand voice + visual identity constants extracted from ledgerproofhq.io.

These are load-bearing — drift here causes off-brand outbound. They are
treated as the single source of truth for rendering.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class BrandColors:
    bg: str = "#FAF7F0"
    navy: str = "#081424"
    mint: str = "#20E898"
    accent_warm: str = "#E8A87C"


@dataclass(frozen=True)
class BrandFonts:
    display: str = "Iowan Old Style, Georgia, serif"
    sans: str = "Inter, system-ui, sans-serif"
    mono: str = "JetBrains Mono, ui-monospace, monospace"


COLORS = BrandColors()
FONTS = BrandFonts()


FORBIDDEN_PHRASES = (
    "hope you're well",
    "hope this finds you well",
    "i noticed your background",
    "quick question",
    "circling back",
    "just checking in",
    "leader in ai compliance",
    "ai safety platform",
    "next big thing",
    "synergy",
    "we believe",
)
"""Phrases that fail brand voice review. The render pipeline rejects copy
containing any of these (case-insensitive).
"""


_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


class BrandVoiceError(ValueError):
    """Raised when rendered copy violates brand voice constraints."""


def validate_copy(text: str) -> None:
    """Raise BrandVoiceError if the rendered copy violates brand constraints."""
    lowered = text.lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase in lowered:
            raise BrandVoiceError(f"forbidden phrase: {phrase!r}")


def reject_pii_in_field(field_name: str, value: str) -> None:
    """GDPR safety net replicating the schema-level rejection at SDK boundary.

    Emails must NOT appear in deployer_id, reviewer_role, or review_rationale.
    The same rule applies to anything that will become part of a published
    Foundation artifact.
    """
    if field_name in {"deployer_id", "reviewer_role", "review_rationale"}:
        if _EMAIL_RE.search(value):
            raise BrandVoiceError(
                f"PII rejection: {field_name!r} contains an email address"
            )
