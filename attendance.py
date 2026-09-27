"""
attendance.py
-------------
Handles marking attendance (DB + CSV) and generating simple
reports that act as the project's "dashboard".
"""

from collections import defaultdict

import database
import utils


def mark(name: str):
    """
    Mark attendance for a known person, once per day.
    Writes to both the SQLite database and the CSV backup.
    Returns True if a new record was created.
    """
    date, time = utils.now_date_time()
    created = database.mark_attendance(name, date, time)

    if created:
        utils.append_to_csv(name, date, time)
        print(f"[✓] Attendance marked: {name} at {time} on {date}")
    return created


def print_report(date: str = None):
    """
    Print a simple text 'dashboard' of attendance.
    If date is given (YYYY-MM-DD), filters to that day; otherwise
    shows everything, grouped by date.
    """
    rows = database.get_attendance(date)

    if not rows:
        print("No attendance records found.")
        return

    grouped = defaultdict(list)
    for name, d, t in rows:
        grouped[d].append((name, t))

    print("\n" + "=" * 50)
    print(" ATTENDANCE REPORT")
    print("=" * 50)

    for d in sorted(grouped.keys(), reverse=True):
        print(f"\nDate: {d}")
        print("-" * 30)
        for name, t in sorted(grouped[d], key=lambda x: x[1]):
            print(f"  {t}   {name}")

    print("\n" + "=" * 50)
    print(f" Total records: {len(rows)}")
    print("=" * 50 + "\n")
