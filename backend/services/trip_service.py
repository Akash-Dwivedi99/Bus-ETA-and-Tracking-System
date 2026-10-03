"""
Trip service — route/bus/stop administration and direction switching.
Used by routes/buses.py, routes/routes.py (the route-resource blueprint),
and routes/driver.py.
"""

from database.db import (
    get_conn,
    fetch_all_buses,
    fetch_all_routes,
    fetch_stops_by_route,
    insert_route,
    insert_bus,
    insert_stop,
    fetch_bus_route_id,
    fetch_paired_route_id,
    update_bus_route,
)


def list_buses():
    conn = get_conn()
    try:
        cursor = conn.cursor(dictionary=True)
        data = fetch_all_buses(cursor)
        cursor.close()
        return data
    finally:
        conn.close()


def register_bus(bus_id, bus_number, route_id):
    conn = get_conn()
    try:
        cursor = conn.cursor()
        insert_bus(cursor, bus_id, bus_number, route_id)
        conn.commit()
        cursor.close()
    finally:
        conn.close()


def list_routes():
    conn = get_conn()
    try:
        cursor = conn.cursor(dictionary=True)
        data = fetch_all_routes(cursor)
        cursor.close()
        return data
    finally:
        conn.close()


def create_route(name):
    conn = get_conn()
    try:
        cursor = conn.cursor()
        new_id = insert_route(cursor, name)
        conn.commit()
        cursor.close()
        return new_id
    finally:
        conn.close()


def list_stops_for_route(route_id):
    conn = get_conn()
    try:
        cursor = conn.cursor(dictionary=True)
        data = fetch_stops_by_route(cursor, route_id)
        cursor.close()
        return data
    finally:
        conn.close()


def add_stop(route_id, name, lat, lng, stop_order):
    conn = get_conn()
    try:
        cursor = conn.cursor()
        new_id = insert_stop(cursor, route_id, name, lat, lng, stop_order)
        conn.commit()
        cursor.close()
        return new_id
    finally:
        conn.close()


def toggle_direction(bus_id):
    """
    Flips a bus between its route's forward and return direction.
    Returns (new_route_id, error_message) — error_message is None on
    success, or a human-readable reason it failed.
    """
    conn = get_conn()
    try:
        cursor = conn.cursor(dictionary=True)

        bus_row = fetch_bus_route_id(cursor, bus_id)
        if not bus_row:
            return None, "bus not found"

        route_row = fetch_paired_route_id(cursor, bus_row["route_id"])
        paired_id = route_row["paired_route_id"] if route_row else None

        if not paired_id:
            return None, (
                "This route has no return-direction route configured. "
                "Check database/schema.sql has run fully."
            )

        update_bus_route(cursor, bus_id, paired_id)
        conn.commit()
        cursor.close()
        return paired_id, None
    finally:
        conn.close()
