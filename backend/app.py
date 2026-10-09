"""Flask application entry point for Campus Transit."""

from datetime import timedelta
from pathlib import Path
import secrets
import sys
from urllib.parse import urlsplit

from flask import Flask, jsonify, request, send_from_directory
from mysql.connector import Error as MySQLError
from werkzeug.middleware.proxy_fix import ProxyFix

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import (  # noqa: E402
    APP_ENV, APP_ORIGIN, DB_CONFIG, DEBUG, PORT, RATELIMIT_STORAGE_URI,
    SECRET_KEY, TRUSTED_PROXY_HOPS,
)
from backend.routes.auth import auth_bp  # noqa: E402
from backend.routes.student import student_bp  # noqa: E402
from backend.routes.driver import driver_bp  # noqa: E402
from backend.routes.buses import buses_bp  # noqa: E402
from backend.routes.routes import routes_bp  # noqa: E402
from backend.routes.tracking import tracking_bp  # noqa: E402

FRONTEND_DIR = PROJECT_ROOT / "frontend"
app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")
LOCAL_FRONTEND_ORIGINS = {
    f"http://{host}:{port}"
    for host in ("localhost", "127.0.0.1")
    for port in ("5500", "5501")
}
origin = urlsplit(APP_ORIGIN)
if TRUSTED_PROXY_HOPS < 0 or TRUSTED_PROXY_HOPS > 3:
    raise RuntimeError("TRUSTED_PROXY_HOPS must be between 0 and 3")
if APP_ENV == "production":
    if len(SECRET_KEY) < 32 or SECRET_KEY.lower() in {"change-me", "changeme", "secret"}:
        raise RuntimeError("Set a unique SECRET_KEY of at least 32 characters for production")
    if not (origin.scheme == "https" and origin.netloc and origin.path == ""):
        raise RuntimeError("APP_ORIGIN must be the HTTPS origin of this application")
    if DB_CONFIG["user"] == "root" or len(DB_CONFIG["password"]) < 16:
        raise RuntimeError("Use a dedicated database account with a strong password in production")

app.config.update(
    SECRET_KEY=SECRET_KEY or secrets.token_hex(32),
    APP_ENV=APP_ENV,
    APP_ORIGIN=APP_ORIGIN,
    RATELIMIT_STORAGE_URI=RATELIMIT_STORAGE_URI,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=APP_ENV == "production",
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
    MAX_CONTENT_LENGTH=180 * 1024,
)
if TRUSTED_PROXY_HOPS:
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=TRUSTED_PROXY_HOPS,
                            x_proto=TRUSTED_PROXY_HOPS, x_host=TRUSTED_PROXY_HOPS)


@app.get("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/healthz")
def healthz():
    return jsonify({"status": "ok"})


@app.get("/readyz")
def readyz():
    from backend.database.db import get_conn
    connection = get_conn()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT 1")
        cursor.fetchone()
    finally:
        cursor.close()
        connection.close()
    return jsonify({"status": "ready"})


@app.after_request
def add_security_headers(response):
    request_origin = request.headers.get("Origin")
    if APP_ENV != "production" and request_origin in LOCAL_FRONTEND_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = request_origin
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.vary.add("Origin")
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Content-Security-Policy", "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'")
    if APP_ENV == "production":
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    return response


@app.errorhandler(MySQLError)
def database_unavailable(_error):
    return jsonify({"error": "Database unavailable. Start MySQL and check BUS_DB_* settings."}), 503


for blueprint in (auth_bp, student_bp, driver_bp, buses_bp, routes_bp, tracking_bp):
    app.register_blueprint(blueprint)


if __name__ == "__main__":
    app.run(debug=DEBUG and APP_ENV != "production", port=PORT)
