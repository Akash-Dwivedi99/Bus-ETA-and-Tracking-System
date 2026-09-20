"""
Simulates a moving bus by posting new GPS coordinates every few seconds.
Run this ALONGSIDE app.py (separate terminal) while the dashboard is open
in your browser — you'll see the bus marker slide smoothly, live.

Usage:
  pip install requests
  python simulate_movement.py
"""

import time
import requests

API_URL = "http://localhost:5000/api/update-location"
BUS_ID = "bus-1"

# A simple straight-line path between two points on your route.
# Replace these with real coordinates from your `stops` table.
START = (30.3256, 78.0437)   # Clock Tower
END = (30.3426, 77.9250)     # College Gate

STEPS = 40          # how many points along the path
DELAY_SECONDS = 4   # gap between each update (keep < POLL_INTERVAL_MS in maps.js)


def lerp(a, b, t):
    return a + (b - a) * t


def main():
    print(f"Simulating {BUS_ID} moving from {START} to {END}...")
    for i in range(STEPS + 1):
        t = i / STEPS
        lat = lerp(START[0], END[0], t)
        lng = lerp(START[1], END[1], t)

        try:
            res = requests.post(API_URL, json={"bus_id": BUS_ID, "lat": lat, "lng": lng})
            print(f"[{i}/{STEPS}] lat={lat:.5f} lng={lng:.5f} -> {res.status_code}")
        except requests.exceptions.ConnectionError:
            print("Could not reach the server — is app.py running?")
            return

        time.sleep(DELAY_SECONDS)

    print("Done. Bus reached the end point.")


if __name__ == "__main__":
    main()