"""
Student blueprint — the endpoint the student dashboard actually polls.
"""

from flask import Blueprint, request, jsonify
from services.eta_service import get_tracking_data

student_bp = Blueprint("student", __name__)


@student_bp.route("/api/bus-location", methods=["GET"])
def bus_location():
    bus_id = request.args.get("bus_id", default="bus-1")

    data = get_tracking_data(bus_id)
    if data is None:
        return jsonify({"error": "No location data yet for this bus"}), 404

    return jsonify(data)
