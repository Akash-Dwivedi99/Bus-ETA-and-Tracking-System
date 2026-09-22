"""
Configuration for the Bus Tracking System backend.
Keep secrets and environment-specific values here — app.py and
database/db.py both read from this file instead of hardcoding values.
"""

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "AkashSQL99",   # <-- replace with your actual MySQL password
    "database": "bus_tracker",
}

# Average bus speed used for ETA estimation when no historical
# speed/trip data exists yet (see Phase 6 in the build guide for the
# future ML-based version of this).
AVG_SPEED_KMPH = 25

# A stop counts as "reached" once the bus is within this many km of it.
REACHED_RADIUS_KM = 0.15  # ~150 meters

# Flask server settings
DEBUG = True
PORT = 5000
