"""
database.py
-----------
Handles all SQLite database operations for the Face Recognition
Attendance System: schema creation, inserting attendance records,
logging unknown-person detections, and querying reports.
"""

import sqlite3
import os
from datetime import datetime

DB_DIR = "database"
DB_PATH = os.path.join(DB_DIR, "attendance.db")


def get_connection():
    """Create the database directory (if needed) and return a connection."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create tables if they don't already exist."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS persons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            image_path TEXT NOT NULL,
            registered_on TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_name TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            UNIQUE(person_name, date)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS unknown_detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_path TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def add_person(name: str, image_path: str):
    """Register a new known person in the database."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO persons (name, image_path, registered_on) VALUES (?, ?, ?)",
            (name, image_path, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"[!] Person '{name}' already registered.")
    finally:
        conn.close()


def has_marked_today(name: str, date: str) -> bool:
    """Check whether a person's attendance is already marked for a given date."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM attendance WHERE person_name = ? AND date = ?", (name, date)
    )
    result = cur.fetchone()
    conn.close()
    return result is not None


def mark_attendance(name: str, date: str, time: str) -> bool:
    """
    Insert an attendance record if not already marked for that date.
    Returns True if a new record was inserted, False if already present.
    """
    if has_marked_today(name, date):
        return False

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO attendance (person_name, date, time) VALUES (?, ?, ?)",
        (name, date, time),
    )
    conn.commit()
    conn.close()
    return True


def log_unknown_detection(image_path: str, date: str, time: str):
    """Record a detection of an unrecognized face."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO unknown_detections (image_path, date, time) VALUES (?, ?, ?)",
        (image_path, date, time),
    )
    conn.commit()
    conn.close()


def get_attendance(date: str = None):
    """Return attendance rows, optionally filtered by date (YYYY-MM-DD)."""
    conn = get_connection()
    cur = conn.cursor()
    if date:
        cur.execute(
            "SELECT person_name, date, time FROM attendance WHERE date = ? ORDER BY time",
            (date,),
        )
    else:
        cur.execute(
            "SELECT person_name, date, time FROM attendance ORDER BY date DESC, time"
        )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_all_persons():
    """Return all registered known persons."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, image_path, registered_on FROM persons")
    rows = cur.fetchall()
    conn.close()
    return rows
