"""
RouteGraph — represents a bus route's stops as a graph (§5.5-5.7 of the
synopsis): nodes are stops, edges are weighted by the distance between
consecutive stops. Built fresh from the `stops` table so it always
reflects whatever is currently in the database.
"""

from algorithms.dijkstra import dijkstra, shortest_path as _shortest_path
from algorithms.eta import haversine_km


class RouteGraph:
    def __init__(self):
        self.adj = {}  # node name -> list of (neighbor name, weight km)

    def add_stop(self, name):
        self.adj.setdefault(name, [])

    def add_edge(self, a, b, weight):
        """Undirected — a route can usually be traveled either way."""
        self.add_stop(a)
        self.add_stop(b)
        self.adj[a].append((b, weight))
        self.adj[b].append((a, weight))

    @classmethod
    def from_stops(cls, stops):
        """
        Builds a graph by connecting consecutive stops (by stop_order)
        with an edge weighted by the real Haversine distance between
        them — so the graph mirrors the actual physical route.

        `stops` is a list of dicts with at least: name, lat, lng,
        stop_order (already sorted by stop_order, as db.fetch_route_stops
        and db.fetch_stops_by_route both return them).
        """
        graph = cls()
        for stop in stops:
            graph.add_stop(stop["name"])

        for i in range(len(stops) - 1):
            a, b = stops[i], stops[i + 1]
            dist = haversine_km(a["lat"], a["lng"], b["lat"], b["lng"])
            graph.add_edge(a["name"], b["name"], dist)

        return graph

    def dijkstra(self, source):
        return dijkstra(self.adj, source)

    def shortest_path(self, source, target):
        return _shortest_path(self.adj, source, target)


if __name__ == "__main__":
    # Standalone demo — run `python algorithms/graph.py` to see it work
    # independently of the Flask app or the database. Good for a viva.
    sample_stops = [
        {"name": "College Gate", "lat": 30.3426, "lng": 77.9250, "stop_order": 1},
        {"name": "Clock Tower", "lat": 30.3256, "lng": 78.0437, "stop_order": 2},
        {"name": "ISBT", "lat": 30.2881, "lng": 77.9990, "stop_order": 3},
    ]
    g = RouteGraph.from_stops(sample_stops)
    path, dist = g.shortest_path("College Gate", "ISBT")
    print(f"Shortest path: {' -> '.join(path)}")
    print(f"Total distance: {dist:.2f} km")
