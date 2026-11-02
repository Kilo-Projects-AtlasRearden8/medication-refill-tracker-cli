"""Tests for the date logic in refill_tracker.dates."""

from datetime import date

import pytest

from refill_tracker.dates import (
    add_days,
    days_until_due,
    due_date,
    is_due,
    parse_date,
)


class TestParseDate:
    def test_valid_iso_date(self):
        assert parse_date("2026-11-02") == date(2026, 11, 2)

    def test_leap_year(self):
        assert parse_date("2024-02-29") == date(2024, 2, 29)

    def test_invalid_returns_none(self):
        assert parse_date("not-a-date") is None
        assert parse_date("") is None
        assert parse_date("2026-13-01") is None  # bad month
        assert parse_date("2026-11-32") is None  # bad day
        assert parse_date(None) is None


class TestAddDays:
    def test_positive_offset(self):
        assert add_days(date(2026, 11, 1), 30) == date(2026, 12, 1)

    def test_negative_offset(self):
        assert add_days(date(2026, 12, 1), -30) == date(2026, 11, 1)

    def test_crosses_year(self):
        assert add_days(date(2026, 12, 25), 10) == date(2027, 1, 4)

    def test_leap_crossover(self):
        assert add_days(date(2024, 2, 28), 1) == date(2024, 2, 29)


class TestDueDate:
    def test_prefers_explicit_next_due(self):
        assert due_date("2026-01-01", 30, next_due="2026-12-25") == date(
            2026, 12, 25
        )

    def test_derives_from_last_filled_and_supply(self):
        assert due_date("2026-11-01", 30) == date(2026, 12, 1)

    def test_returns_none_when_insufficient(self):
        assert due_date(None, 30) is None
        assert due_date("2026-11-01", 0) is None
        assert due_date(None, 0) is None

    def test_bad_last_filled_returns_none(self):
        assert due_date("not-a-date", 30) is None


class TestIsDue:
    def test_due_on_reference_is_true(self):
        assert is_due(date(2026, 11, 2), reference=date(2026, 11, 2)) is True

    def test_due_before_reference_is_true(self):
        assert is_due(date(2026, 11, 1), reference=date(2026, 11, 2)) is True

    def test_due_after_reference_is_false(self):
        assert is_due(date(2026, 11, 3), reference=date(2026, 11, 2)) is False

    def test_none_is_not_due(self):
        assert is_due(None) is False


class TestDaysUntilDue:
    def test_positive_remaining(self):
        assert days_until_due(date(2026, 11, 10), reference=date(2026, 11, 2)) == 8

    def test_zero_on_due_date(self):
        assert days_until_due(date(2026, 11, 2), reference=date(2026, 11, 2)) == 0

    def test_negative_when_overdue(self):
        assert days_until_due(date(2026, 11, 1), reference=date(2026, 11, 2)) == -1

    def test_none_returns_none(self):
        assert days_until_due(None) is None
