"""One-off migration: convert old string dates ('2026-1-5') to datetime objects.

Usage:
    python migrate_dates.py           # dry run, only prints what would change
    python migrate_dates.py --apply   # writes the changes
"""
import argparse
import datetime

from database import get_collection


def parse_old_date(value):
    year, month, day = (int(part) for part in value.split("-"))
    return datetime.datetime(year, month, day, tzinfo=datetime.timezone.utc)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--apply", action="store_true", help="write the changes to the database")
    args = parser.parse_args()

    collection = get_collection()
    changed = skipped = 0
    for item in collection.find({"date": {"$type": "string"}}):
        try:
            new_date = parse_old_date(item["date"])
        except ValueError:
            print(f"Skipping {item['_id']}: unknown date format {item['date']!r}")
            skipped += 1
            continue
        if args.apply:
            collection.update_one({"_id": item["_id"]}, {"$set": {"date": new_date}})
        changed += 1

    action = "Converted" if args.apply else "Would convert"
    print(f"{action} {changed} item(s), skipped {skipped}.")
    if not args.apply and changed:
        print("Run again with --apply to write the changes.")


if __name__ == "__main__":
    main()
