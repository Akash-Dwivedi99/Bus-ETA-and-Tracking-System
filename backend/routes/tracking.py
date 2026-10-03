"""
Tracking blueprint — fleet-wide position queries, distinct from
student.py's single-bus ETA tracking. Not called by the current
frontend yet; scaffolded for a future "all buses at once" admin map.
"""

from flask import Blueprint, jsonify
from services.eta_service import get_all_bus_positions

tracking_bp = Blueprint("tracking", __name__)


@tracking_bp.route("/api/tracking/all", methods=["GET"])
def all_positions():
    return jsonify(get_all_bus_positions())
