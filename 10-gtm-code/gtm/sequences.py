"""Outbound timing rules.

The plan's cadence is non-negotiable:
- Send window: Tuesday or Wednesday, 09:00–10:30 Brussels time
- Never Monday (inbox triage), never Friday (deferred to Monday)
- 7 business days of silence → switch persona at the same account
- 14 business days of silence → switch to written-only artifact send
- Two-touch cap per individual; the third touch is an artifact or a warm intro
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

import pytz

BRUSSELS = pytz.timezone("Europe/Brussels")

SEND_WINDOW_OPEN = time(9, 0)
SEND_WINDOW_CLOSE = time(10, 30)
SEND_DAYS = (1, 2)  # Tuesday, Wednesday (Mon=0, Sun=6)

PERSONA_SWITCH_BD = 7
ARTIFACT_ONLY_BD = 14
INDIVIDUAL_CAP = 2


class SendWindowError(ValueError):
    """Raised when a requested send time is outside policy."""


def is_business_day(d: date) -> bool:
    return d.weekday() < 5


def add_business_days(start: date, n: int) -> date:
    """Add n business days to start (skipping weekends)."""
    d = start
    added = 0
    step = 1 if n >= 0 else -1
    target = abs(n)
    while added < target:
        d = d + timedelta(days=step)
        if is_business_day(d):
            added += 1
    return d


def business_days_between(a: date, b: date) -> int:
    """Count business days between two dates (b - a)."""
    if b < a:
        return -business_days_between(b, a)
    days = 0
    d = a
    while d < b:
        d = d + timedelta(days=1)
        if is_business_day(d):
            days += 1
    return days


def is_send_day(d: date) -> bool:
    return d.weekday() in SEND_DAYS


def next_send_slot(after: datetime | None = None) -> datetime:
    """Return the next allowed send datetime in Brussels TZ."""
    now = after or datetime.now(tz=BRUSSELS)
    if now.tzinfo is None:
        now = BRUSSELS.localize(now)
    else:
        now = now.astimezone(BRUSSELS)

    candidate_date = now.date()
    for _ in range(14):
        if is_send_day(candidate_date):
            slot = BRUSSELS.localize(
                datetime.combine(candidate_date, SEND_WINDOW_OPEN)
            )
            if slot > now:
                return slot
        candidate_date = candidate_date + timedelta(days=1)
    raise SendWindowError("no send slot found in the next 14 days")


def validate_send_time(when: datetime, force: bool = False) -> None:
    """Validate a proposed send time against policy. Raise unless force=True."""
    local = when.astimezone(BRUSSELS) if when.tzinfo else BRUSSELS.localize(when)
    if not is_send_day(local.date()):
        if not force:
            raise SendWindowError(
                f"{local.date().isoformat()} is not Tue/Wed (Brussels)"
            )
    if not (SEND_WINDOW_OPEN <= local.time() <= SEND_WINDOW_CLOSE):
        if not force:
            raise SendWindowError(
                f"{local.time().isoformat()} is outside 09:00–10:30 CET"
            )


@dataclass
class TouchPolicy:
    """Per-account cadence policy."""

    last_touch: date | None
    touches_to_individual: int
    today: date

    def needs_persona_switch(self) -> bool:
        if self.last_touch is None:
            return False
        return business_days_between(self.last_touch, self.today) >= PERSONA_SWITCH_BD

    def needs_artifact_only(self) -> bool:
        if self.last_touch is None:
            return False
        return business_days_between(self.last_touch, self.today) >= ARTIFACT_ONLY_BD

    def at_cap(self) -> bool:
        return self.touches_to_individual >= INDIVIDUAL_CAP
