"""
Buses blueprint — list buses (used by every dashboard's picker) and
register new ones (admin panel).
"""

from flask import Blueprint, request, jsonify
from backend.services.trip_service import list_buses, register_bus

buses_bp = Blueprint("buses", __name__)


@buses_bp.route("/api/buses", methods=["GET"])
def get_buses():
    return jsonify(list_buses())


@buses_bp.route("/api/buses", methods=["POST"])
def create_bus():
    data = request.get_json(silent=True) or {}
    bus_id = data.get("id")
    bus_number = data.get("bus_number")
    route_id = data.get("route_id")

    if not bus_id or not bus_number or not route_id:
        return jsonify({"error": "id, bus_number and route_id are required"}), 400

    register_bus(bus_id, bus_number, route_id)
    return jsonify({"id": bus_id, "bus_number": bus_number, "route_id": route_id}), 201
