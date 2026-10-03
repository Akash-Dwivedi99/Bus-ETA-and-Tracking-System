"""
Routes blueprint (for the "route" resource — a bus route and its stops,
not to be confused with this folder's own name). Used by the admin
panel and the Dijkstra/graph endpoints.
"""

from flask import Blueprint, request, jsonify
from backend.services.trip_service import list_routes, create_route, list_stops_for_route, add_stop
from backend.database.db import get_conn, fetch_route_stops
from backend.algorithms.graph import RouteGraph

routes_bp = Blueprint("routes", __name__)


@routes_bp.route("/api/routes", methods=["GET"])
def get_routes():
    return jsonify(list_routes())


@routes_bp.route("/api/routes", methods=["POST"])
def create_route_route():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    if not name:
        return jsonify({"error": "name is required"}), 400

    new_id = create_route(name)
    return jsonify({"id": new_id, "name": name}), 201


@routes_bp.route("/api/routes/<int:route_id>/stops", methods=["GET"])
def get_route_stops(route_id):
    return jsonify(list_stops_for_route(route_id))


@routes_bp.route("/api/stops", methods=["POST"])
def create_stop():
    data = request.get_json(silent=True) or {}
    route_id = data.get("route_id")
    name = data.get("name")
    lat = data.get("lat")
    lng = data.get("lng")
    stop_order = data.get("stop_order")

    if None in (route_id, name, lat, lng, stop_order):
        return jsonify({"error": "route_id, name, lat, lng and stop_order are required"}), 400

    new_id = add_stop(route_id, name, lat, lng, stop_order)
    return jsonify({"id": new_id, "route_id": route_id, "name": name}), 201


@routes_bp.route("/api/routes/<int:route_id>/shortest-path", methods=["GET"])
def shortest_path_route(route_id):
    """
    Dijkstra demo endpoint: ?from=<stop name>&to=<stop name>
    Builds the route's graph from real stop data and returns the
    shortest path between two of its stops. Mainly useful for a viva
    demo of the DSA component — the student dashboard doesn't call this.
    """
    from_stop = request.args.get("from")
    to_stop = request.args.get("to")
    if not from_stop or not to_stop:
        return jsonify({"error": "from and to query params are required"}), 400

    conn = get_conn()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, name, lat, lng, stop_order FROM stops WHERE route_id = %s ORDER BY stop_order",
            (route_id,),
        )
        stops = cursor.fetchall()
        cursor.close()
    finally:
        conn.close()

    graph = RouteGraph.from_stops(stops)
    path, distance = graph.shortest_path(from_stop, to_stop)

    if path is None:
        return jsonify({"error": f"No path found between '{from_stop}' and '{to_stop}'"}), 404

    return jsonify({"path": path, "distance_km": round(distance, 2)})
