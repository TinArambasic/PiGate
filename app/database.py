import sqlite3
from datetime import datetime

import os
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gate.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS allowed_plates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate_number TEXT UNIQUE NOT NULL,
            owner_name TEXT,
            added_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate_number TEXT NOT NULL,
            recognized BOOLEAN NOT NULL,
            confidence REAL,
            direction TEXT,
            timestamp TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def add_plate(plate_number, owner_name=""):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO allowed_plates (plate_number, owner_name, added_at) VALUES (?, ?, ?)",
            (plate_number.upper().replace(" ", ""), owner_name, datetime.now().isoformat())
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def remove_plate(plate_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM allowed_plates WHERE id = ?", (plate_id,))
    conn.commit()
    conn.close()

def get_all_plates():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM allowed_plates ORDER BY added_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def is_plate_allowed(plate_number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM allowed_plates WHERE plate_number = ?",
        (plate_number.upper().replace(" ", ""),)
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None

def log_access(plate_number, recognized, confidence=None, direction="entry"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO access_logs (plate_number, recognized, confidence, direction, timestamp) VALUES (?, ?, ?, ?, ?)",
        (plate_number, recognized, confidence, direction, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_logs(limit=100):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM access_logs ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
