"""Date logic helpers used by the refill tracker.

Pure functions with no side effects — easy to test and reason about.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta


def parse_date(value: str) -> date | None:
    """Parse an ISO 8601 date string (YYYY-MM-DD). Returns None on bad input."""
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def add_days(base: date, days: int) -> date:
    return base + timedelta(days=days)


def due_date(last_filled: str | None, days_supply: int, next_due: str | None = None) -> date | None:
    """Compute the next due date.

    Prefers an explicit ``next_due`` when given, otherwise derives it from
    ``last_filled`` + ``days_supply``. Returns None when nothing can be
    computed.
    """
    if next_due:
        return parse_date(next_due)
    if last_filled and days_supply:
        base = parse_date(last_filled)
        if base:
            return add_days(base, days_supply)
    return None


def is_due(due: date | None, reference: date | None = None) -> bool:
    if due is None:
        return False
    ref = reference or date.today()
    return due <= ref


def days_until_due(due: date | None, reference: date | None = None) -> int | None:
    if due is None:
        return None
    ref = reference or date.today()
    return (due - ref).days
