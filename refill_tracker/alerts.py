"""Due-date alert logic (education only, not medical advice)."""
from __future__ import annotations

from datetime import date, timedelta

from .models import Prescription


def parse_date(value: str) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def status_for(prescription: Prescription, today: date | None = None) -> dict:
    today = today or date.today()
    next_refill = parse_date(prescription.next_refill_date)
    if next_refill is None:
        computed = prescription.compute_next_refill_date()
        next_refill = parse_date(computed or "")
    overdue = next_refill is not None and next_refill < today
    due_soon = (
        next_refill is not None
        and not overdue
        and next_refill <= today + timedelta(days=7)
    )
    return {
        "prescription": prescription,
        "next_refill_date": next_refill.isoformat() if next_refill else None,
        "overdue": overdue,
        "due_soon": due_soon,
        "days_until_refill": (next_refill - today).days if next_refill else None,
    }


def upcoming_alerts(
    prescriptions: list[Prescription],
    today: date | None = None,
    within_days: int = 7,
) -> list[dict]:
    today = today or date.today()
    results = []
    for prescription in prescriptions:
        hit = status_for(prescription, today)
        if hit["overdue"] or (
            hit["due_soon"]
            and hit["days_until_refill"] is not None
            and hit["days_until_refill"] <= within_days
        ):
            results.append(hit)
    results.sort(key=lambda h: h["next_refill_date"] or "")
    return results
