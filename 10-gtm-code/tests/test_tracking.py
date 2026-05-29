from datetime import datetime

from gtm.tracking import (
    Account,
    AccountStatus,
    Contact,
    Touch,
    TouchKind,
    TouchOutcome,
    find_account,
    find_contact,
    init_db,
    last_touch_to_account,
    session,
    touches_for_contact,
)


def test_init_creates_tables() -> None:
    init_db()
    with session() as s:
        # Trivial insert/query proves the schema is live.
        s.add(Account(name="Test Corp", sector="banking", jurisdiction="DE"))
        s.commit()
        found = find_account(s, "Test Corp")
        assert found is not None
        assert found.status == AccountStatus.PROSPECT


def test_contact_lookup_by_persona() -> None:
    init_db()
    with session() as s:
        acct = Account(name="Bank A", sector="banking", jurisdiction="DE")
        s.add(acct)
        s.commit()
        s.refresh(acct)
        s.add(
            Contact(
                account_id=acct.id,
                name="J. Doe",
                title="GC",
                persona="gc",
                email="redacted@example.com",
            )
        )
        s.commit()
        c = find_contact(s, acct.id, "gc")
        assert c is not None
        assert c.persona == "gc"
        # Persona that does not exist returns None
        assert find_contact(s, acct.id, "mlops") is None


def test_last_touch_ordering() -> None:
    init_db()
    with session() as s:
        acct = Account(name="Bank B", sector="banking", jurisdiction="FR")
        s.add(acct)
        s.commit()
        s.refresh(acct)
        contact = Contact(
            account_id=acct.id,
            name="K",
            title="GC",
            persona="gc",
            email="r@example.com",
        )
        s.add(contact)
        s.commit()
        s.refresh(contact)
        s.add_all(
            [
                Touch(
                    account_id=acct.id,
                    contact_id=contact.id,
                    when=datetime(2026, 7, 14, 9, 0),
                    kind=TouchKind.EMAIL,
                    persona="gc",
                    artifact_slug="outbound_email_gc",
                    subject="first",
                    body_hash="a" * 64,
                    receipt_id="mock-a",
                    outcome=TouchOutcome.SENT,
                ),
                Touch(
                    account_id=acct.id,
                    contact_id=contact.id,
                    when=datetime(2026, 7, 28, 9, 0),
                    kind=TouchKind.EMAIL,
                    persona="cro_cco",
                    artifact_slug="outbound_email_cro_cco",
                    subject="second",
                    body_hash="b" * 64,
                    receipt_id="mock-b",
                    outcome=TouchOutcome.SENT,
                ),
            ]
        )
        s.commit()

        last = last_touch_to_account(s, acct.id)
        assert last is not None
        assert last.subject == "second"
        assert len(touches_for_contact(s, contact.id)) == 2
