# STATUS — Medication Refill Tracker CLI

## What was built

A local-first Python CLI for tracking prescriptions, refill dates, and pharmacy
contacts, with due-date alerts and local JSON/CSV export. Built for Asdale
Dynamics, LLC as an accessible life-admin / healthcare-worker aid (education
only, never medical advice).

Files:
- `refill_tracker/__init__.py` — package marker, version 0.1.0
- `refill_tracker/models.py` — `Prescription` and `PharmacyContact` dataclasses;
  due-date computation, overdue detection, days-until-due
- `refill_tracker/dates.py` — pure date helpers (parse, add days, due date, is
  due, days until due) with no side effects
- `refill_tracker/storage.py` — `Store` class: JSON persistence, CRUD, due
  filtering, JSON/CSV export, CSV import
- `refill_tracker/cli.py` — `med-refill` CLI: add, list, due, show, remove,
  pharmacy-add, pharmacy-list, export, import; prints education disclaimer on
  every run
- `tests/test_dates.py` — 19 tests covering all date logic
- `pyproject.toml` — project metadata, `med-refill` console script entry point
- `LICENSE` — MIT, copyright line exactly `Copyright (c) 2026 Asdale Dynamics, LLC`
- `README.md` — usage, quick start, disclaimer, Asdale Dynamics credit
- `.gitignore` — standard Python ignores

No `.github/workflows` files. No secrets, API keys, or personal data. No
network calls; all data stays in a local JSON file.

## How to run

```bash
# From the project folder
pip install -e .        # (or use python3 -m refill_tracker.cli without install)

med-refill --help

med-refill add "Lisinopril 10mg" \
  --last-filled 2026-10-01 --days-supply 30 \
  --pharmacy "Corner Pharmacy" --refills-remaining 2

med-refill list --due-only
med-refill due 2026-11-15
med-refill export backup.json
med-refill export backup.csv --format csv
med-refill import backup.csv
```

Default data file is `refills.json` in the current folder; override with
`--data-file`.

## Verification results

- `pytest`: 19 passed (all date-logic tests), 0.01s
- CLI end-to-end exercised: add, list, due (past/future reference dates), show,
  export (JSON and CSV), import — all behave correctly
- Education disclaimer prints on every invocation
- No external dependencies (stdlib only); no network, no keys

## Known gaps

- No test coverage yet for CLI commands or `Store` CRUD (only date logic is
  tested).
- No deduplication guard on CSV import (re-importing creates duplicate rows).
- `pip install -e .` requires `--break-system-packages` on externally managed
  Python environments; use a venv or `python3 -m refill_tracker.cli` instead.
- Windows not tested; paths use `os.path` so should be portable.

Git initialized and committed once as `d289c98` (identity: Dylan Asdale /
dylanasdale@users.noreply.github.com). Not pushed, no remote created.
