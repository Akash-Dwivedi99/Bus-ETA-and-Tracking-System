"""
Dijkstra's shortest-path algorithm — standalone, graph-structure-agnostic.

Works on a plain adjacency dict: {node: [(neighbor, weight), ...]}.
graph.py's RouteGraph builds that structure from stops and calls this;
keeping the algorithm itself separate makes it independently testable
and reusable outside the RouteGraph class.
"""

import heapq


def dijkstra(adj, source):
    """
    Returns (distances, previous) from `source` to every other node in
    the graph.

    Steps:
      1. distance[source] = 0, all others = infinity
      2. repeatedly pick the unvisited node with smallest known distance
      3. relax its neighbors (update their distance if a shorter path
         through this node was just found)
      4. mark it visited, repeat until the priority queue is empty
    """
    distances = {node: float("inf") for node in adj}
    previous = {node: None for node in adj}
    distances[source] = 0
    visited = set()
    pq = [(0, source)]  # (distance, node) — a min-heap priority queue

    while pq:
        dist_u, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)

        for v, weight in adj[u]:
            new_dist = dist_u + weight
            if new_dist < distances[v]:
                distances[v] = new_dist
                previous[v] = u
                heapq.heappush(pq, (new_dist, v))

    return distances, previous


def shortest_path(adj, source, target):
    """Reconstructs the actual path (list of nodes) and its total
    distance from `source` to `target`, or (None, inf) if unreachable."""
    distances, previous = dijkstra(adj, source)
    if distances[target] == float("inf"):
        return None, float("inf")

    path = []
    node = target
    while node is not None:
        path.append(node)
        node = previous[node]
    path.reverse()
    return path, distances[target]
