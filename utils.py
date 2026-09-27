"""
utils.py
--------
Small shared helper functions used across the project.
"""

import os
import csv
from datetime import datetime

CSV_DIR = "attendance"
CSV_PATH = os.path.join(CSV_DIR, "attendance.csv")


def now_date_time():
    """Return (date_str, time_str) for the current moment."""
    now = datetime.now()
    return now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")


def ensure_dirs():
    """Make sure all required project directories exist."""
    for d in ("known_faces", "attendance", "database", "unknown_faces"):
        os.makedirs(d, exist_ok=True)


def append_to_csv(name: str, date: str, time: str):
    """Append a single attendance record to the CSV backup file."""
    os.makedirs(CSV_DIR, exist_ok=True)
    file_exists = os.path.isfile(CSV_PATH)

    with open(CSV_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Name", "Date", "Time"])
        writer.writerow([name, date, time])


def valid_image_file(filename: str) -> bool:
    """Check whether a filename has a supported image extension."""
    return filename.lower().endswith((".jpg", ".jpeg", ".png"))
