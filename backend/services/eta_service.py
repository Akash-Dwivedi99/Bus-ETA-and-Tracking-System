"""
ETA service — orchestrates the student dashboard's main query:
"where is the bus, which stops has it passed, and when will it arrive?"

This is the layer that ties algorithms/eta.py's pure math to real data
from the database.
"""

from database.db import get_conn, fetch_route_stops
from algorithms.eta import haversine_km, build_stop_payload
from services.location_service import get_latest_location


def get_tracking_data(bus_id):
    """
    Returns the full payload the student dashboard polls, or None if
    the bus has no location yet (route handler turns that into a 404).
    """
    latest = get_latest_location(bus_id)
    if not latest:
        return None

    conn = get_conn()
    try:
        cursor = conn.cursor(dictionary=True)
        stops = fetch_route_stops(cursor, bus_id)
        cursor.close()
    finally:
        conn.close()

    stop_payload = build_stop_payload(stops, latest["lat"], latest["lng"])
    next_stop = next((s for s in stop_payload if s["next"]), None)

    return {
        "bus": {"lat": latest["lat"], "lng": latest["lng"]},
        "stops": stop_payload,
        "eta_min": next_stop["eta_min"] if next_stop else None,
        "next_stop_name": next_stop["name"] if next_stop else None,
        "distance_km": round(
            haversine_km(latest["lat"], latest["lng"], next_stop["lat"], next_stop["lng"]), 2
        ) if next_stop else None,
        "last_updated": latest["recorded_at"].isoformat(),
    }


def get_all_bus_positions():
    """
    Raw current position of every bus (no ETA calculation) — a lighter
    query than get_tracking_data, meant for a future fleet-overview view
    (e.g. an admin map showing every bus at once) rather than per-bus
    ETA tracking.
    """
    from database.db import fetch_all_buses

    conn = get_conn()
    try:
        cursor = conn.cursor(dictionary=True)
        buses = fetch_all_buses(cursor)
        cursor.close()
    finally:
        conn.close()

    positions = []
    for bus in buses:
        latest = get_latest_location(bus["id"])
        positions.append({
            "bus_id": bus["id"],
            "bus_number": bus["bus_number"],
            "route_name": bus["route_name"],
            "lat": latest["lat"] if latest else None,
            "lng": latest["lng"] if latest else None,
            "last_updated": latest["recorded_at"].isoformat() if latest else None,
        })
    return positions
