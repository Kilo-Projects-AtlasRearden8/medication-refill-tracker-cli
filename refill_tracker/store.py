"""Local JSON persistence and CSV/JSON export."""
from __future__ import annotations

import csv
import json
import os

from .models import Pharmacy, Prescription


class Store:
    def __init__(self, path: str):
        self.path = path
        self.pharmacies: dict[str, Pharmacy] = {}
        self.prescriptions: dict[str, Prescription] = {}
        self._loaded = False

    def load(self) -> None:
        if self._loaded:
            return
        if not os.path.exists(self.path):
            self._loaded = True
            return
        with open(self.path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        for item in data.get("pharmacies", []):
            pharmacy = Pharmacy.from_dict(item)
            self.pharmacies[pharmacy.id] = pharmacy
        for item in data.get("prescriptions", []):
            prescription = Prescription.from_dict(item)
            self.prescriptions[prescription.id] = prescription
        self._loaded = True

    def save(self) -> None:
        directory = os.path.dirname(os.path.abspath(self.path))
        if directory:
            os.makedirs(directory, exist_ok=True)
        data = {
            "pharmacies": [p.to_dict() for p in self.pharmacies.values()],
            "prescriptions": [p.to_dict() for p in self.prescriptions.values()],
        }
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)

    def add_pharmacy(self, pharmacy: Pharmacy) -> None:
        self.load()
        self.pharmacies[pharmacy.id] = pharmacy
        self.save()

    def add_prescription(self, prescription: Prescription) -> None:
        self.load()
        self.prescriptions[prescription.id] = prescription
        self.save()

    def list_pharmacies(self) -> list[Pharmacy]:
        self.load()
        return sorted(self.pharmacies.values(), key=lambda p: p.name.lower())

    def list_prescriptions(self) -> list[Prescription]:
        self.load()
        return sorted(self.prescriptions.values(), key=lambda p: p.name.lower())

    def find_pharmacy_by_name(self, name: str) -> Pharmacy | None:
        self.load()
        for pharmacy in self.pharmacies.values():
            if pharmacy.name.lower() == name.lower():
                return pharmacy
        return None

    def export_csv(self, path: str) -> None:
        self.load()
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(
                [
                    "id",
                    "name",
                    "dosage",
                    "frequency",
                    "pharmacy_id",
                    "start_date",
                    "refill_every_days",
                    "last_filled_date",
                    "next_refill_date",
                    "notes",
                ]
            )
            for prescription in self.list_prescriptions():
                writer.writerow(
                    [
                        prescription.id,
                        prescription.name,
                        prescription.dosage,
                        prescription.frequency,
                        prescription.pharmacy_id,
                        prescription.start_date,
                        prescription.refill_every_days,
                        prescription.last_filled_date,
                        prescription.next_refill_date,
                        prescription.notes,
                    ]
                )

    def export_json(self, path: str) -> None:
        self.load()
        data = {
            "pharmacies": [p.to_dict() for p in self.list_pharmacies()],
            "prescriptions": [p.to_dict() for p in self.list_prescriptions()],
        }
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
