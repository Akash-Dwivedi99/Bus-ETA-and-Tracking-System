"""
ETA math — distance calculation and the reached/next/upcoming stop logic.
Pure functions, no database or Flask imports, so they're easy to test
on their own.
"""

from math import radians, sin, cos, sqrt, atan2
from config import AVG_SPEED_KMPH, REACHED_RADIUS_KM


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
    of how far the bus has since driven from it. A plain proximity check
    (distance <= radius) breaks once the bus drives further than the
    radius away from a stop it already passed — the stop would stop
    counting as "reached" and get re-picked as "next", with its distance
    climbing as the bus drives further away.
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
