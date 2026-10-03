"""
Location service — recording and reading GPS points.
Wraps database/db.py with connection handling, so routes/*.py never
opens a MySQL connection directly.
"""

from datetime import datetime
from backend.database.db import get_conn, insert_bus_location, fetch_latest_location


def record_location(bus_id, lat, lng):
    """Driver app's GPS ping lands here."""
    conn = get_conn()
    try:
        cursor = conn.cursor()
        insert_bus_location(cursor, bus_id, lat, lng, datetime.utcnow())
        conn.commit()
        cursor.close()
    finally:
        conn.close()


def get_latest_location(bus_id):
    """Returns {lat, lng, recorded_at} for a bus, or None if it has
    never reported a location."""
    conn = get_conn()
    try:
        cursor = conn.cursor(dictionary=True)
        latest = fetch_latest_location(cursor, bus_id)
        cursor.close()
        return latest
    finally:
        conn.close()
