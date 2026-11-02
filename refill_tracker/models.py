"""Data models for prescriptions, refills, and pharmacy contacts.

All dates are stored as ISO 8601 strings (YYYY-MM-DD). No secrets, API keys,
or personal data are ever written to disk beyond what the user provides.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from typing import Optional


@dataclass
class PharmacyContact:
    """A pharmacy contact the user manages locally."""

    name: str
    phone: str = ""
    address: str = ""
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "PharmacyContact":
        return cls(
            name=data.get("name", ""),
            phone=data.get("phone", ""),
            address=data.get("address", ""),
            notes=data.get("notes", ""),
        )


@dataclass
class Prescription:
    """A single prescription the user tracks locally.

    Fields are intentionally simple and beginner-friendly. None of this data
    is medical advice — it is only a reminder aid the user controls.
    """

    id: str
    name: str
    dosage: str = ""
    frequency: str = ""
    pharmacy: str = ""
    last_filled: Optional[str] = None
    days_supply: int = 30
    refills_remaining: int = 0
    next_due: Optional[str] = None
    notes: str = ""

    def due_date(self) -> Optional[date]:
        """Return the computed next-due date, or None if not set."""
        if self.next_due:
            return _parse_date(self.next_due)
        if self.last_filled and self.days_supply:
            base = _parse_date(self.last_filled)
            if base:
                return _add_days(base, self.days_supply)
        return None

    def is_due(self, reference: Optional[date] = None) -> bool:
        """True if the prescription is due on or before ``reference`` (today
        by default)."""
        due = self.due_date()
        if due is None:
            return False
        ref = reference or date.today()
        return due <= ref

    def days_until_due(self, reference: Optional[date] = None) -> Optional[int]:
        """Days remaining until due (negative means already overdue)."""
        due = self.due_date()
        if due is None:
            return None
        ref = reference or date.today()
        return (due - ref).days

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Prescription":
        return cls(
            id=str(data.get("id", "")),
            name=str(data.get("name", "")),
            dosage=str(data.get("dosage", "")),
            frequency=str(data.get("frequency", "")),
            pharmacy=str(data.get("pharmacy", "")),
            last_filled=data.get("last_filled"),
            days_supply=int(data.get("days_supply", 30) or 30),
            refills_remaining=int(data.get("refills_remaining", 0) or 0),
            next_due=data.get("next_due"),
            notes=str(data.get("notes", "")),
        )


def _parse_date(value: str) -> Optional[date]:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _add_days(base: date, days: int) -> date:
    from datetime import timedelta

    return base + timedelta(days=days)
