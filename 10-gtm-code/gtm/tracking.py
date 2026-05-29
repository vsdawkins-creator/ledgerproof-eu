"""SQLite-backed state for outbound tracking.

A single database file (~/.lpr-gtm/state.db by default; override via
LPR_GTM_DB env var) holds Accounts, Contacts, and Touches.

Every Touch is also anchored as a LedgerProof Receipt (see anchoring.py).
"""

from __future__ import annotations

import os
from datetime import date, datetime
from enum import StrEnum
from pathlib import Path
from typing import List, Optional

from sqlmodel import Field, Session, SQLModel, create_engine, select


def _db_path() -> Path:
    override = os.environ.get("LPR_GTM_DB")
    if override:
        return Path(override).expanduser()
    home = Path.home() / ".lpr-gtm"
    home.mkdir(parents=True, exist_ok=True)
    return home / "state.db"


def get_engine(db_path: Path | None = None):
    path = db_path or _db_path()
    return create_engine(f"sqlite:///{path}", echo=False)


class AccountStatus(StrEnum):
    PROSPECT = "prospect"
    ENGAGED = "engaged"
    PILOT = "pilot"
    PRODUCTION = "production"
    DECLINED = "declined"
    DO_NOT_CONTACT = "do_not_contact"


class TouchKind(StrEnum):
    EMAIL = "email"
    ARTIFACT = "artifact"
    WARM_INTRO = "warm_intro"
    REFERENCE_CALL = "reference_call"


class TouchOutcome(StrEnum):
    SENT = "sent"
    REPLIED = "replied"
    BOUNCED = "bounced"
    OOO = "ooo"
    BOOKED = "booked"
    DECLINED = "declined"


class Account(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    sector: str
    jurisdiction: str
    tier: int = Field(default=1)
    status: AccountStatus = Field(default=AccountStatus.PROSPECT)
    notes: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Contact(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="account.id", index=True)
    name: str
    title: str
    persona: str = Field(index=True)  # PersonaSlug value
    email: str
    linkedin: str = ""
    verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Touch(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="account.id", index=True)
    contact_id: int = Field(foreign_key="contact.id", index=True)
    when: datetime = Field(index=True)
    kind: TouchKind
    persona: str = Field(index=True)
    artifact_slug: str
    subject: str
    body_hash: str = Field(description="SHA-256 of rendered body")
    receipt_id: str = Field(default="", description="LedgerProof Receipt ID once anchored")
    bitcoin_block: Optional[int] = Field(default=None)
    outcome: TouchOutcome = Field(default=TouchOutcome.SENT)
    notes: str = ""


def init_db(db_path: Path | None = None) -> None:
    SQLModel.metadata.create_all(get_engine(db_path))


def session(db_path: Path | None = None) -> Session:
    return Session(get_engine(db_path))


# -------- convenience queries --------


def find_account(s: Session, name: str) -> Optional[Account]:
    return s.exec(select(Account).where(Account.name == name)).first()


def find_contact(s: Session, account_id: int, persona: str) -> Optional[Contact]:
    return s.exec(
        select(Contact).where(
            Contact.account_id == account_id, Contact.persona == persona
        )
    ).first()


def touches_for_contact(s: Session, contact_id: int) -> List[Touch]:
    return list(s.exec(select(Touch).where(Touch.contact_id == contact_id)).all())


def last_touch_to_account(s: Session, account_id: int) -> Optional[Touch]:
    return s.exec(
        select(Touch)
        .where(Touch.account_id == account_id)
        .order_by(Touch.when.desc())
    ).first()


def touches_on_date(s: Session, d: date) -> List[Touch]:
    start = datetime.combine(d, datetime.min.time())
    end = datetime.combine(d, datetime.max.time())
    return list(
        s.exec(select(Touch).where(Touch.when >= start, Touch.when <= end)).all()
    )
