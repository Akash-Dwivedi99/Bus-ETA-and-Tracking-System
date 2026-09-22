"""
Bus Tracking System — Flask Backend
------------------------------------
Endpoints:
  POST /api/update-location            -> driver app pushes live GPS coordinates
  GET  /api/bus-location                -> student dashboard polls current bus + stop + ETA data
  GET  /api/stops                       -> list all stops for a bus's route
  POST /api/stops                       -> admin: add a stop to a route
  GET  /api/buses                       -> list all buses + their route name
  POST /api/buses                       -> admin: register a new bus
  GET  /api/routes                      -> list all routes
  POST /api/routes                      -> admin: create a new route
  GET  /api/routes/<id>/stops           -> all stops for a route, by route_id directly
  POST /api/buses/<id>/toggle-direction -> driver: flip a bus to its route's return direction

Run:
  pip install flask flask-cors mysql-connector-python
  python app.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime

from config import AVG_SPEED_KMPH, REACHED_RADIUS_KM, DEBUG, PORT
from database.db import (
    get_conn,
    fetch_latest_location,
    fetch_route_stops,
    fetch_stops_by_route,
    fetch_all_buses,
    fetch_all_routes,
    insert_bus_location,
    insert_route,
    insert_bus,
    insert_stop,
    fetch_bus_route_id,
    fetch_paired_route_id,
    update_bus_route,
)

app = Flask(__name__)
CORS(app)  # allow the dashboard (served from a different origin/port) to call this API


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

    distances = [haversine_km(bus_lat, bus_lng, s["lat"], s["lng"]) for s in stops]
    closest_idx = min(range(len(stops)), key=lambda i: distances[i])

    payload = []
    next_stop_found = False
    cumulative_km_to_next = None

    for i, stop in enumerate(stops):
        if i < closest_idx:
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
        insert_bus_location(cursor, bus_id, lat, lng, datetime.utcnow())
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


@app.route("/api/buses", methods=["POST"])
def create_bus():
    """Admin panel: register a new bus against an existing route."""
    data = request.get_json(silent=True) or {}
    bus_id = data.get("id")
    bus_number = data.get("bus_number")
    route_id = data.get("route_id")

    if not bus_id or not bus_number or not route_id:
        return jsonify({"error": "id, bus_number and route_id are required"}), 400

    conn = get_conn()
    try:
        cursor = conn.cursor()
        insert_bus(cursor, bus_id, bus_number, route_id)
        conn.commit()
        cursor.close()
    finally:
        conn.close()
    return jsonify({"id": bus_id, "bus_number": bus_number, "route_id": route_id}), 201


@app.route("/api/routes", methods=["GET"])
def routes():
    """List every route — used by the admin panel and driver.html."""
    conn = get_conn()
    try:
        cursor = conn.cursor(dictionary=True)
        data = fetch_all_routes(cursor)
        cursor.close()
    finally:
        conn.close()
    return jsonify(data)


@app.route("/api/routes", methods=["POST"])
def create_route():
    """Admin panel: create a new route."""
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    if not name:
        return jsonify({"error": "name is required"}), 400

    conn = get_conn()
    try:
        cursor = conn.cursor()
        new_id = insert_route(cursor, name)
        conn.commit()
        cursor.close()
    finally:
        conn.close()
    return jsonify({"id": new_id, "name": name}), 201


@app.route("/api/routes/<int:route_id>/stops", methods=["GET"])
def route_stops(route_id):
    """All stops for a route, directly by route_id — used by the admin panel."""
    conn = get_conn()
    try:
        cursor = conn.cursor(dictionary=True)
        data = fetch_stops_by_route(cursor, route_id)
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


@app.route("/api/stops", methods=["POST"])
def create_stop():
    """Admin panel: add a stop to a route."""
    data = request.get_json(silent=True) or {}
    route_id = data.get("route_id")
    name = data.get("name")
    lat = data.get("lat")
    lng = data.get("lng")
    stop_order = data.get("stop_order")

    if None in (route_id, name, lat, lng, stop_order):
        return jsonify({"error": "route_id, name, lat, lng and stop_order are required"}), 400

    conn = get_conn()
    try:
        cursor = conn.cursor()
        new_id = insert_stop(cursor, route_id, name, lat, lng, stop_order)
        conn.commit()
        cursor.close()
    finally:
        conn.close()
    return jsonify({"id": new_id, "route_id": route_id, "name": name}), 201


@app.route("/api/buses/<bus_id>/toggle-direction", methods=["POST"])
def toggle_direction(bus_id):
    """Driver page: flip a bus between a route's forward and return direction."""
    conn = get_conn()
    try:
        cursor = conn.cursor(dictionary=True)

        bus_row = fetch_bus_route_id(cursor, bus_id)
        if not bus_row:
            return jsonify({"error": "bus not found"}), 404

        route_row = fetch_paired_route_id(cursor, bus_row["route_id"])
        paired_id = route_row["paired_route_id"] if route_row else None

        if not paired_id:
            return jsonify({
                "error": "This route has no return-direction route configured. "
                         "Check database/schema.sql has run fully."
            }), 400

        update_bus_route(cursor, bus_id, paired_id)
        conn.commit()
        cursor.close()
    finally:
        conn.close()

    return jsonify({"status": "ok", "bus_id": bus_id, "new_route_id": paired_id})


if __name__ == "__main__":
    app.run(debug=DEBUG, port=PORT)
