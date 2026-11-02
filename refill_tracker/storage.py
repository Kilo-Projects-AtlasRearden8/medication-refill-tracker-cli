"""Local-first storage for prescriptions and pharmacy contacts.

Supports JSON and CSV export/import. All data stays on the user's machine —
no network calls, no keys, no cloud sync.
"""

from __future__ import annotations

import csv
import json
import os
from typing import List, Optional

from .models import PharmacyContact, Prescription


class Store:
    """A file-backed store of prescriptions and pharmacy contacts."""

    def __init__(self, path: str) -> None:
        self.path = path
        self.prescriptions: List[Prescription] = []
        self.pharmacies: List[PharmacyContact] = []
        self._loaded = False

    # ------------------------------------------------------------------ load

    def load(self) -> None:
        """Load data from the JSON file at ``self.path`` if it exists."""
        if self._loaded:
            return
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
            except (json.JSONDecodeError, OSError):
                data = {}
            self.prescriptions = [
                Prescription.from_dict(item) for item in data.get("prescriptions", [])
            ]
            self.pharmacies = [
                PharmacyContact.from_dict(item) for item in data.get("pharmacies", [])
            ]
        self._loaded = True

    # ------------------------------------------------------------------ save

    def save(self) -> None:
        """Persist prescriptions and pharmacies to the JSON file."""
        data = {
            "prescriptions": [p.to_dict() for p in self.prescriptions],
            "pharmacies": [p.to_dict() for p in self.pharmacies],
        }
        directory = os.path.dirname(os.path.abspath(self.path))
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        tmp_path = self.path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, sort_keys=True)
        os.replace(tmp_path, self.path)

    # ------------------------------------------------------------------ CRUD

    def add_prescription(self, prescription: Prescription) -> None:
        self.load()
        self.prescriptions.append(prescription)
        self.save()

    def add_pharmacy(self, pharmacy: PharmacyContact) -> None:
        self.load()
        self.pharmacies.append(pharmacy)
        self.save()

    def find_prescription(self, pid: str) -> Optional[Prescription]:
        self.load()
        for p in self.prescriptions:
            if p.id == pid:
                return p
        return None

    def remove_prescription(self, pid: str) -> bool:
        self.load()
        before = len(self.prescriptions)
        self.prescriptions = [p for p in self.prescriptions if p.id != pid]
        if len(self.prescriptions) < before:
            self.save()
            return True
        return False

    def due_prescriptions(
        self, reference=None
    ) -> List[Prescription]:
        """Return prescriptions that are due on or before ``reference``."""
        self.load()
        return [p for p in self.prescriptions if p.is_due(reference)]

    # ------------------------------------------------------------------ export

    def export_json(self, path: str) -> None:
        self.load()
        data = {
            "prescriptions": [p.to_dict() for p in self.prescriptions],
            "pharmacies": [p.to_dict() for p in self.pharmacies],
        }
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, sort_keys=True)

    def export_csv(self, path: str) -> None:
        """Export prescriptions to CSV (flat, beginner-friendly)."""
        self.load()
        fieldnames = [
            "id",
            "name",
            "dosage",
            "frequency",
            "pharmacy",
            "last_filled",
            "days_supply",
            "refills_remaining",
            "next_due",
            "notes",
        ]
        with open(path, "w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            for p in self.prescriptions:
                row = p.to_dict()
                writer.writerow({k: row.get(k, "") for k in fieldnames})

    def import_csv(self, path: str) -> int:
        """Import prescriptions from CSV. Returns number imported."""
        self.load()
        imported = 0
        with open(path, "r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                self.prescriptions.append(Prescription.from_dict(row))
                imported += 1
        self.save()
        return imported
