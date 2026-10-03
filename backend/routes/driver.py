"""
Driver blueprint — everything the driver page's "Start Trip" and
"Switch direction" buttons call.
"""

from flask import Blueprint, request, jsonify
from services.location_service import record_location
from services.trip_service import toggle_direction

driver_bp = Blueprint("driver", __name__)


@driver_bp.route("/api/update-location", methods=["POST"])
def update_location():
    data = request.get_json(silent=True) or {}
    bus_id = data.get("bus_id")
    lat = data.get("lat")
    lng = data.get("lng")

    if bus_id is None or lat is None or lng is None:
        return jsonify({"error": "bus_id, lat and lng are required"}), 400

    record_location(bus_id, lat, lng)
    return jsonify({"status": "ok"}), 200


@driver_bp.route("/api/buses/<bus_id>/toggle-direction", methods=["POST"])
def toggle_direction_route(bus_id):
    new_route_id, error = toggle_direction(bus_id)
    if error:
        status = 404 if error == "bus not found" else 400
        return jsonify({"error": error}), status

    return jsonify({"status": "ok", "bus_id": bus_id, "new_route_id": new_route_id})
