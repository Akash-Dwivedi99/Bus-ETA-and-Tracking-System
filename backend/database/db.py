"""
Database access layer.
Everything that touches MySQL directly lives here — app.py calls these
functions instead of writing SQL inline, so the query logic is in one
place and testable on its own.
"""

from mysql.connector import pooling
from config import DB_CONFIG

pool = pooling.MySQLConnectionPool(pool_name="bus_pool", pool_size=5, **DB_CONFIG)


def get_conn():
    return pool.get_connection()


def fetch_latest_location(cursor, bus_id):
    """Most recent GPS point for a bus."""
    cursor.execute(
        """
        SELECT lat, lng, recorded_at
        FROM bus_locations
        WHERE bus_id = %s
        ORDER BY recorded_at DESC
        LIMIT 1
        """,
        (bus_id,),
    )
    return cursor.fetchone()


def fetch_route_stops(cursor, bus_id):
    """All stops for whichever route a bus is currently assigned to,
    in order."""
    cursor.execute(
        """
        SELECT s.id, s.name, s.lat, s.lng, s.stop_order
        FROM stops s
        JOIN routes r ON r.id = s.route_id
        JOIN buses b ON b.route_id = r.id
        WHERE b.id = %s
        ORDER BY s.stop_order ASC
        """,
        (bus_id,),
    )
    return cursor.fetchall()


def fetch_stops_by_route(cursor, route_id):
    """All stops for a route, directly by route_id — used by the admin
    panel (a route may not have a bus assigned yet, so fetch_route_stops's
    bus join won't find it)."""
    cursor.execute(
        "SELECT id, name, lat, lng, stop_order FROM stops WHERE route_id = %s ORDER BY stop_order",
        (route_id,),
    )
    return cursor.fetchall()


def fetch_all_buses(cursor):
    """All buses with their route name — used to build the dashboard's
    bus/route picker dynamically instead of hardcoding options in HTML."""
    cursor.execute(
        """
        SELECT b.id, b.bus_number, r.name AS route_name
        FROM buses b
        JOIN routes r ON r.id = b.route_id
        ORDER BY b.id
        """
    )
    return cursor.fetchall()


def fetch_all_routes(cursor):
    cursor.execute("SELECT id, name, paired_route_id FROM routes ORDER BY id")
    return cursor.fetchall()


def insert_bus_location(cursor, bus_id, lat, lng, recorded_at):
    cursor.execute(
        "INSERT INTO bus_locations (bus_id, lat, lng, recorded_at) VALUES (%s, %s, %s, %s)",
        (bus_id, lat, lng, recorded_at),
    )


def insert_route(cursor, name):
    cursor.execute("INSERT INTO routes (name) VALUES (%s)", (name,))
    return cursor.lastrowid


def insert_bus(cursor, bus_id, bus_number, route_id):
    cursor.execute(
        "INSERT INTO buses (id, bus_number, route_id) VALUES (%s, %s, %s)",
        (bus_id, bus_number, route_id),
    )


def insert_stop(cursor, route_id, name, lat, lng, stop_order):
    cursor.execute(
        "INSERT INTO stops (route_id, name, lat, lng, stop_order) VALUES (%s, %s, %s, %s, %s)",
        (route_id, name, lat, lng, stop_order),
    )
    return cursor.lastrowid


def fetch_bus_route_id(cursor, bus_id):
    cursor.execute("SELECT route_id FROM buses WHERE id = %s", (bus_id,))
    return cursor.fetchone()


def fetch_paired_route_id(cursor, route_id):
    cursor.execute("SELECT paired_route_id FROM routes WHERE id = %s", (route_id,))
    return cursor.fetchone()


def update_bus_route(cursor, bus_id, route_id):
    cursor.execute("UPDATE buses SET route_id = %s WHERE id = %s", (route_id, bus_id))
