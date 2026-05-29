from datetime import date

import pytest

from gtm.brand import BrandVoiceError
from gtm.personas import PersonaSlug
from gtm.rendering import render_email, render_one_pager


def test_render_email_gc_includes_account() -> None:
    email = render_email(
        persona=PersonaSlug.GC,
        account_name="Deutsche Bank",
        contact_name="A",
        contact_title="General Counsel",
        send_date=date(2026, 7, 28),
    )
    assert email.subject.startswith("A Board Pack PDF")
    assert "Deutsche Bank" in email.body
    assert email.persona == PersonaSlug.GC
    assert len(email.body_hash) == 64


def test_render_email_cro_includes_enforcement_countdown() -> None:
    email = render_email(
        persona=PersonaSlug.CRO_CCO,
        account_name="Allianz",
        contact_name="B",
        contact_title="Chief Risk Officer",
        send_date=date(2026, 7, 28),  # 5 days to enforcement
    )
    assert "5 days" in email.subject
    assert "Allianz" in email.body


def test_render_email_mlops_classifies_50_4() -> None:
    email = render_email(
        persona=PersonaSlug.MLOPS,
        account_name="Vodafone",
        contact_name="C",
        contact_title="Head of AI Infrastructure",
        send_date=date(2026, 7, 28),
    )
    assert email.article50_subclause == "50(4)"


def test_render_email_hashes_are_deterministic() -> None:
    a = render_email(
        persona=PersonaSlug.GC,
        account_name="Deutsche Bank",
        contact_name="X",
        contact_title="GC",
        send_date=date(2026, 7, 28),
    )
    b = render_email(
        persona=PersonaSlug.GC,
        account_name="Deutsche Bank",
        contact_name="X",
        contact_title="GC",
        send_date=date(2026, 7, 28),
    )
    assert a.body_hash == b.body_hash


def test_render_email_hashes_differ_by_account() -> None:
    a = render_email(
        persona=PersonaSlug.GC,
        account_name="Deutsche Bank",
        contact_name="X",
        contact_title="GC",
        send_date=date(2026, 7, 28),
    )
    b = render_email(
        persona=PersonaSlug.GC,
        account_name="BNP Paribas",
        contact_name="X",
        contact_title="GC",
        send_date=date(2026, 7, 28),
    )
    assert a.body_hash != b.body_hash


def test_render_one_pager_shadow_inventory_has_critical_anchors() -> None:
    md = render_one_pager("shadow_ai_inventory")
    assert "Shadow AI Inventory" in md
    assert "inventory@ledgerproofhq.io" in md
    assert "verify.ledgerproofhq.io" in md
