from datetime import date, datetime

import pytest
from freezegun import freeze_time

from gtm import sequences
from gtm.sequences import (
    BRUSSELS,
    SendWindowError,
    TouchPolicy,
    add_business_days,
    business_days_between,
    is_business_day,
    is_send_day,
    next_send_slot,
    validate_send_time,
)


def test_is_business_day_weekday() -> None:
    assert is_business_day(date(2026, 7, 28))  # Tuesday


def test_is_business_day_weekend() -> None:
    assert not is_business_day(date(2026, 8, 1))  # Saturday


def test_is_send_day_tuesday() -> None:
    assert is_send_day(date(2026, 7, 28))


def test_is_send_day_wednesday() -> None:
    assert is_send_day(date(2026, 7, 29))


@pytest.mark.parametrize("d", [date(2026, 7, 27), date(2026, 7, 30), date(2026, 7, 31)])
def test_is_send_day_other(d: date) -> None:
    assert not is_send_day(d)


def test_add_business_days_skips_weekend() -> None:
    # Friday + 1 business day = Monday
    assert add_business_days(date(2026, 7, 31), 1) == date(2026, 8, 3)


def test_business_days_between_spans_weekend() -> None:
    assert business_days_between(date(2026, 7, 28), date(2026, 8, 4)) == 5


@freeze_time("2026-07-25 12:00:00", tz_offset=0)
def test_next_send_slot_from_saturday_returns_tuesday() -> None:
    slot = next_send_slot()
    assert slot.weekday() == 1  # Tuesday
    assert slot.date() == date(2026, 7, 28)
    assert slot.hour == 9


@freeze_time("2026-07-28 11:00:00", tz_offset=0)
def test_next_send_slot_after_window_returns_wednesday() -> None:
    # 11:00 UTC = 13:00 CEST → past window; next slot is Wed 09:00 CEST
    slot = next_send_slot()
    assert slot.date() == date(2026, 7, 29)


def test_validate_send_time_rejects_monday() -> None:
    monday = BRUSSELS.localize(datetime(2026, 7, 27, 9, 0))
    with pytest.raises(SendWindowError):
        validate_send_time(monday)


def test_validate_send_time_rejects_friday() -> None:
    friday = BRUSSELS.localize(datetime(2026, 7, 31, 9, 0))
    with pytest.raises(SendWindowError):
        validate_send_time(friday)


def test_validate_send_time_accepts_tuesday_window() -> None:
    tue = BRUSSELS.localize(datetime(2026, 7, 28, 9, 30))
    validate_send_time(tue)  # no exception


def test_validate_send_time_force_overrides() -> None:
    friday = BRUSSELS.localize(datetime(2026, 7, 31, 9, 0))
    validate_send_time(friday, force=True)  # no exception


def test_touch_policy_persona_switch_threshold() -> None:
    policy = TouchPolicy(
        last_touch=date(2026, 7, 14),
        touches_to_individual=1,
        today=date(2026, 7, 28),
    )
    # 10 business days have elapsed; should switch
    assert policy.needs_persona_switch()


def test_touch_policy_no_switch_when_recent() -> None:
    policy = TouchPolicy(
        last_touch=date(2026, 7, 24),
        touches_to_individual=1,
        today=date(2026, 7, 28),
    )
    # 2 business days; below the 7 threshold
    assert not policy.needs_persona_switch()


def test_touch_policy_artifact_only_threshold() -> None:
    policy = TouchPolicy(
        last_touch=date(2026, 7, 7),
        touches_to_individual=1,
        today=date(2026, 7, 28),
    )
    # 15 business days elapsed; over 14 → artifact-only mode
    assert policy.needs_artifact_only()


def test_touch_policy_at_cap() -> None:
    policy = TouchPolicy(
        last_touch=None,
        touches_to_individual=2,
        today=date.today(),
    )
    assert policy.at_cap()
