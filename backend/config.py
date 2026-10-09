"""
Configuration for the Bus Tracking System backend.
Keep secrets and environment-specific values here — app.py and
database/db.py both read from this file instead of hardcoding values.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=False)

DB_CONFIG = {
    "host": os.getenv("BUS_DB_HOST", "localhost"),
    "port": int(os.getenv("BUS_DB_PORT", "3306")),
    "user": os.getenv("BUS_DB_USER", "root"),
    "password": os.getenv("BUS_DB_PASSWORD", ""),
    "database": os.getenv("BUS_DB_NAME", "bus_tracker"),
}

# Average bus speed used for ETA estimation when no historical
# speed/trip data exists yet (see Phase 6 in the build guide for the
# future ML-based version of this).
AVG_SPEED_KMPH = 25

# A stop counts as "reached" once the bus is within this many km of it.
REACHED_RADIUS_KM = 0.15  # ~150 meters

# Flask server settings
DEBUG = os.getenv("FLASK_DEBUG", "0").lower() in ("1", "true", "yes")
PORT = int(os.getenv("PORT", "5000"))
APP_ENV = os.getenv("APP_ENV", "development").lower()
TRUSTED_PROXY_HOPS = int(os.getenv("TRUSTED_PROXY_HOPS", "0"))
APP_ORIGIN = os.getenv("APP_ORIGIN", f"http://127.0.0.1:{PORT}")
SECRET_KEY = os.getenv("SECRET_KEY", "")
RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")
