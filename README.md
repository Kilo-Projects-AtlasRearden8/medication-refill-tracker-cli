# Medication Refill Tracker

A local-first, beginner-friendly CLI for tracking prescriptions, refill dates,
and pharmacy contacts — with due-date alerts and local JSON/CSV export.

Built and maintained by **Asdale Dynamics, LLC** (Indiana, formed October 2026).
Part of the LLC's line of accessible life-admin helpers and healthcare-worker AI
aids: practical tools that are education only, never medical advice.

> **DISCLAIMER:** This tool is for education and personal organization only. It
> is NOT medical advice. Always consult a licensed healthcare professional
> before making any medication decisions. Asdale Dynamics, LLC makes no
> representations about the accuracy or suitability of this tool.

## Who this is for

Anyone who wants a simple, private way to keep track of medications and refill
dates without signing up for anything, without an API key, and without data
leaving their computer. Especially useful for busy healthcare workers, caregivers,
and anyone managing multiple prescriptions. Plain English, step by step, never
condescending — in the spirit of Dylan Asdale's *The Massive AI Manual* and the
Asdale Dynamics hub at dylanasdale.github.io.

## Features

- Track prescriptions: name, dosage, frequency, pharmacy, last fill date, days
  supply, refills remaining, notes
- Compute next-due dates from last fill + days supply, or set an explicit due
  date
- Due-date alerts: list prescriptions due today or earlier, or due by any
  reference date you choose
- Pharmacy contact list (name, phone, address, notes)
- Local JSON storage — nothing goes to the cloud, no keys, no network
- Export to JSON or CSV; import prescriptions from CSV
- Pure-Python, no dependencies beyond the standard library
- Tested date logic

## Install

From the project folder:

```bash
pip install -e .
```

This makes the `med-refill` command available on your PATH.

## Quick start

Add a prescription:

```bash
med-refill add "Lisinopril 10mg" \
  --last-filled 2026-10-01 \
  --days-supply 30 \
  --pharmacy "Corner Pharmacy" \
  --refills-remaining 2 \
  --notes "Take with food"
```

List all prescriptions:

```bash
med-refill list
```

Show only what's due today or earlier:

```bash
med-refill list --due-only
```

See what's due by a specific date:

```bash
med-refill due 2026-11-15
```

Add a pharmacy contact:

```bash
med-refill pharmacy-add "Corner Pharmacy" \
  --phone "555-0100" \
  --address "123 Main St, Indianapolis, IN"
```

Export your data (JSON default, or `--format csv`):

```bash
med-refill export my-backup.json
med-refill export my-backup.csv --format csv
```

Import prescriptions from CSV:

```bash
med-refill import my-backup.csv
```

## Data file

By default everything is stored in `refills.json` in the folder where you run
the command. Use `--data-file` to pick a different path. The file is plain JSON
and yours to open, copy, or delete at any time.

## Testing

```bash
pip install pytest
pytest
```

All tests cover the date logic (parsing, offsetting, due-date computation,
overdue detection). There are no external services or secrets involved.

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC.

See `LICENSE` for full text.

## Credit

Created by Asdale Dynamics, LLC — beginner-friendly AI education, books and
guides, and practical open-source tools. Learn more at dylanasdale.github.io.
