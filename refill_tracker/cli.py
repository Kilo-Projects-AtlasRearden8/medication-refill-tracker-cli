"""Command-line interface for the Medication Refill Tracker.

Local-first, beginner-friendly, education only — never medical advice.
Run ``med-refill --help`` to see available commands.
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional, Sequence

from .models import Prescription, PharmacyContact
from .storage import Store
from .dates import due_date, is_due, days_until_due, parse_date

DISCLAIMER = (
    "DISCLAIMER: This tool is for education and personal organization only. "
    "It is NOT medical advice. Always consult a licensed healthcare professional "
    "before making any medication decisions. Asdale Dynamics, LLC makes no "
    "representations about the accuracy or suitability of this tool."
)


def _today_iso() -> str:
    from datetime import date

    return date.today().isoformat()


def cmd_add(args: argparse.Namespace, store: Store) -> int:
    pid = args.id or args.name.lower().replace(" ", "-")
    next_due = args.next_due
    if not next_due and args.last_filled:
        computed = due_date(args.last_filled, args.days_supply)
        next_due = computed.isoformat() if computed else None
    prescription = Prescription(
        id=pid,
        name=args.name,
        dosage=args.dosage,
        frequency=args.frequency,
        pharmacy=args.pharmacy,
        last_filled=args.last_filled,
        days_supply=args.days_supply,
        refills_remaining=args.refills_remaining,
        next_due=next_due,
        notes=args.notes,
    )
    store.add_prescription(prescription)
    print(f"Added prescription '{args.name}' (id={pid}).")
    if next_due:
        print(f"  Next due: {next_due}")
    else:
        print("  Next due: not set (provide --last-filled and --days-supply or --next-due).")
    return 0


def cmd_list(args: argparse.Namespace, store: Store) -> int:
    store.load()
    items = store.prescriptions
    if args.due_only:
        from datetime import date

        items = [p for p in items if p.is_due(date.today())]
    if not items:
        print("No prescriptions found.")
        return 0
    print(f"{'ID':<12} {'Name':<24} {'Due':<12} {'Status':<10} {'Pharmacy'}")
    print("-" * 70)
    from datetime import date as _date

    today = _date.today()
    for p in items:
        due = p.due_date()
        due_str = due.isoformat() if due else "-"
        status = "DUE" if p.is_due(today) else ("OK" if due else "-")
        print(
            f"{p.id:<12} {p.name:<24} {due_str:<12} {status:<10} {p.pharmacy}"
        )
    return 0


def cmd_due(args: argparse.Namespace, store: Store) -> int:
    from datetime import date

    reference = parse_date(args.reference) if args.reference else date.today()
    due_items = store.due_prescriptions(reference)
    if not due_items:
        print(f"No prescriptions due on or before {reference.isoformat()}.")
        return 0
    print(f"Prescriptions due on or before {reference.isoformat()}:")
    print("-" * 60)
    for p in due_items:
        days = days_until_due(p.due_date(), reference)
        print(f"  {p.id:<10} {p.name:<26} due {p.due_date().isoformat()} ({days} days)")
    print("\n" + DISCLAIMER)
    return 0


def cmd_show(args: argparse.Namespace, store: Store) -> int:
    store.load()
    p = store.find_prescription(args.id)
    if not p:
        print(f"No prescription with id '{args.id}'.")
        return 1
    print(f"ID:        {p.id}")
    print(f"Name:      {p.name}")
    print(f"Dosage:    {p.dosage or '-'}")
    print(f"Frequency: {p.frequency or '-'}")
    print(f"Pharmacy:  {p.pharmacy or '-'}")
    print(f"Last filled: {p.last_filled or '-'}")
    print(f"Days supply: {p.days_supply}")
    print(f"Refills remaining: {p.refills_remaining}")
    print(f"Next due:    {p.next_due or '-'}")
    print(f"Notes:     {p.notes or '-'}")
    return 0


def cmd_remove(args: argparse.Namespace, store: Store) -> int:
    if store.remove_prescription(args.id):
        print(f"Removed prescription '{args.id}'.")
        return 0
    print(f"No prescription with id '{args.id}'.")
    return 1


def cmd_add_pharmacy(args: argparse.Namespace, store: Store) -> int:
    pharmacy = PharmacyContact(
        name=args.name,
        phone=args.phone,
        address=args.address,
        notes=args.notes,
    )
    store.add_pharmacy(pharmacy)
    print(f"Added pharmacy '{args.name}'.")
    return 0


def cmd_list_pharmacies(args: argparse.Namespace, store: Store) -> int:
    store.load()
    if not store.pharmacies:
        print("No pharmacy contacts found.")
        return 0
    print(f"{'Name':<24} {'Phone':<16} {'Address'}")
    print("-" * 60)
    for ph in store.pharmacies:
        print(f"{ph.name:<24} {ph.phone:<16} {ph.address}")
    return 0


def cmd_export(args: argparse.Namespace, store: Store) -> int:
    store.load()
    if args.format == "json":
        store.export_json(args.output)
    else:
        store.export_csv(args.output)
    print(f"Exported to {args.output} ({args.format}).")
    return 0


def cmd_import(args: argparse.Namespace, store: Store) -> int:
    count = store.import_csv(args.input)
    print(f"Imported {count} prescription(s) from {args.input}.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="med-refill",
        description="Local-first prescription and refill-date tracker. "
        "Education only — never medical advice.",
    )
    parser.add_argument(
        "--data-file",
        default="refills.json",
        help="Path to the local JSON data file (default: refills.json).",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # add
    p_add = sub.add_parser("add", help="Add a prescription.")
    p_add.add_argument("name", help="Medication name.")
    p_add.add_argument("--id", help="Unique id (default: slug of name).")
    p_add.add_argument("--dosage", default="")
    p_add.add_argument("--frequency", default="")
    p_add.add_argument("--pharmacy", default="")
    p_add.add_argument("--last-filled", dest="last_filled", default="",
                       help="Last fill date (YYYY-MM-DD).")
    p_add.add_argument("--days-supply", type=int, default=30)
    p_add.add_argument("--refills-remaining", type=int, default=0)
    p_add.add_argument("--next-due", dest="next_due", default="",
                       help="Explicit next due date (YYYY-MM-DD).")
    p_add.add_argument("--notes", default="")
    p_add.set_defaults(func=cmd_add)

    # list
    p_list = sub.add_parser("list", help="List prescriptions.")
    p_list.add_argument("--due-only", action="store_true",
                        help="Show only prescriptions due today or earlier.")
    p_list.set_defaults(func=cmd_list)

    # due
    p_due = sub.add_parser("due", help="Show prescriptions due by a date.")
    p_due.add_argument("reference", nargs="?", default="",
                       help="Reference date (YYYY-MM-DD), defaults to today.")
    p_due.set_defaults(func=cmd_due)

    # show
    p_show = sub.add_parser("show", help="Show details of one prescription.")
    p_show.add_argument("id", help="Prescription id.")
    p_show.set_defaults(func=cmd_show)

    # remove
    p_rm = sub.add_parser("remove", help="Remove a prescription by id.")
    p_rm.add_argument("id", help="Prescription id.")
    p_rm.set_defaults(func=cmd_remove)

    # pharmacy add
    p_ph = sub.add_parser("pharmacy-add", help="Add a pharmacy contact.")
    p_ph.add_argument("name", help="Pharmacy name.")
    p_ph.add_argument("--phone", default="")
    p_ph.add_argument("--address", default="")
    p_ph.add_argument("--notes", default="")
    p_ph.set_defaults(func=cmd_add_pharmacy)

    # pharmacy list
    p_pl = sub.add_parser("pharmacy-list", help="List pharmacy contacts.")
    p_pl.set_defaults(func=cmd_list_pharmacies)

    # export
    p_ex = sub.add_parser("export", help="Export data to JSON or CSV.")
    p_ex.add_argument("output", help="Output file path.")
    p_ex.add_argument("--format", choices=["json", "csv"], default="json")
    p_ex.set_defaults(func=cmd_export)

    # import
    p_im = sub.add_parser("import", help="Import prescriptions from CSV.")
    p_im.add_argument("input", help="Input CSV file path.")
    p_im.set_defaults(func=cmd_import)

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    print(DISCLAIMER)
    print()
    parser = build_parser()
    args = parser.parse_args(argv)
    store = Store(args.data_file)
    return args.func(args, store)


if __name__ == "__main__":
    sys.exit(main())
