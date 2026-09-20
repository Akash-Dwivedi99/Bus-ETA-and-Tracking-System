"""
Bus Tracking System — Flask Backend
------------------------------------
Endpoints:
  POST /api/update-location   -> driver app pushes live GPS coordinates
  GET  /api/bus-location      -> student dashboard polls current bus + stop + ETA data
  GET  /api/stops             -> list all stops for a route (static reference data)
  GET  /api/buses             -> list all buses + their route name (populates the dashboard's dropdown dynamically)

Run:
  pip install flask flask-cors mysql-connector-python
  python app.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import pooling
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime

app = Flask(__name__)
CORS(app)  # allow the dashboard (served from a different origin/port) to call this API

# ---------------------------------------------------------------------------
# Database configuration
# ---------------------------------------------------------------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "AkashSQL99",
    "database": "bus_tracker",
}

pool = pooling.MySQLConnectionPool(pool_name="bus_pool", pool_size=5, **DB_CONFIG)

# Average bus speed used for ETA estimation when no historical speed data exists yet.
AVG_SPEED_KMPH = 25


def get_conn():
    return pool.get_connection()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def haversine_km(lat1, lng1, lat2, lng2):
    """Great-circle distance between two lat/lng points, in kilometers."""
    R = 6371.0
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lng2 - lng1)
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def fetch_latest_location(cursor, bus_id):
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


def build_stop_payload(stops, bus_lat, bus_lng):
    """
    Walks the ordered stop list and figures out which stops are already
    reached vs. upcoming.

    Anchored on whichever stop is CLOSEST to the bus right now: every
    earlier stop (by stop_order) is treated as already passed, regardless
    of how far the bus has since driven from it. This matters because a
    plain proximity check (distance <= radius) breaks once the bus drives
    more than the radius away from a stop it already passed — the stop
    would stop counting as "reached" and get re-picked as "next", with
    its distance climbing as the bus drives further away.
    """
    if not stops:
        return []

    REACHED_RADIUS_KM = 0.15  # ~150m counts as "arrived"

    distances = [haversine_km(bus_lat, bus_lng, s["lat"], s["lng"]) for s in stops]
    closest_idx = min(range(len(stops)), key=lambda i: distances[i])

    payload = []
    next_stop_found = False
    cumulative_km_to_next = None

    for i, stop in enumerate(stops):
        if i < closest_idx:
            # Earlier than the closest stop in route order — already passed,
            # no matter how far away the bus has since driven.
            reached, is_next, eta_min = True, False, None

        elif i == closest_idx:
            reached = distances[i] <= REACHED_RADIUS_KM
            is_next = not reached
            eta_min = None
            if is_next:
                eta_min = round((distances[i] / AVG_SPEED_KMPH) * 60, 1)
                cumulative_km_to_next = distances[i]
                next_stop_found = True

        else:
            reached = False
            if not next_stop_found:
                is_next = True
                next_stop_found = True
                cumulative_km_to_next = distances[i]
                eta_min = round((distances[i] / AVG_SPEED_KMPH) * 60, 1)
            else:
                # rough sequential estimate for stops further down the route
                is_next = False
                prev_stop = stops[i - 1]
                leg_km = haversine_km(prev_stop["lat"], prev_stop["lng"], stop["lat"], stop["lng"])
                cumulative_km_to_next += leg_km
                eta_min = round((cumulative_km_to_next / AVG_SPEED_KMPH) * 60, 1)

        payload.append(
            {
                "name": stop["name"],
                "lat": stop["lat"],
                "lng": stop["lng"],
                "reached": reached,
                "next": is_next,
                "eta_min": eta_min,
            }
        )

    return payload


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/api/update-location", methods=["POST"])
def update_location():
    """Driver app calls this every few seconds with live GPS coordinates."""
    data = request.get_json(silent=True) or {}
    bus_id = data.get("bus_id")
    lat = data.get("lat")
    lng = data.get("lng")

    if bus_id is None or lat is None or lng is None:
        return jsonify({"error": "bus_id, lat and lng are required"}), 400

    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO bus_locations (bus_id, lat, lng, recorded_at) VALUES (%s, %s, %s, %s)",
            (bus_id, lat, lng, datetime.utcnow()),
        )
        conn.commit()
        cursor.close()
    finally:
        conn.close()

    return jsonify({"status": "ok"}), 200


@app.route("/api/bus-location", methods=["GET"])
def bus_location():
    """Student dashboard polls this for the bus's current position, stops, and ETA."""
    bus_id = request.args.get("bus_id", default="bus-1")

    conn = get_conn()
    try:
        cursor = conn.cursor(dictionary=True)

        latest = fetch_latest_location(cursor, bus_id)
        if not latest:
            return jsonify({"error": "No location data yet for this bus"}), 404

        stops = fetch_route_stops(cursor, bus_id)
        stop_payload = build_stop_payload(stops, latest["lat"], latest["lng"])

        next_stop = next((s for s in stop_payload if s["next"]), None)

        cursor.close()
    finally:
        conn.close()

    return jsonify(
        {
            "bus": {"lat": latest["lat"], "lng": latest["lng"]},
            "stops": stop_payload,
            "eta_min": next_stop["eta_min"] if next_stop else None,
            "next_stop_name": next_stop["name"] if next_stop else None,
            "distance_km": round(
                haversine_km(
                    latest["lat"], latest["lng"],
                    next_stop["lat"], next_stop["lng"]
                ), 2
            ) if next_stop else None,
            "last_updated": latest["recorded_at"].isoformat(),
        }
    )


@app.route("/api/buses", methods=["GET"])
def buses():
    """List every bus + its route name, so the dashboard's dropdown
    can build itself from the database instead of being hardcoded."""
    conn = get_conn()
    try:
        cursor = conn.cursor(dictionary=True)
        data = fetch_all_buses(cursor)
        cursor.close()
    finally:
        conn.close()

    return jsonify(data)


@app.route("/api/stops", methods=["GET"])
def stops():
    """Static reference data: full stop list for a given bus's route."""
    bus_id = request.args.get("bus_id", default="bus-1")

    conn = get_conn()
    try:
        cursor = conn.cursor(dictionary=True)
        data = fetch_route_stops(cursor, bus_id)
        cursor.close()
    finally:
        conn.close()

    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True, port=5000)