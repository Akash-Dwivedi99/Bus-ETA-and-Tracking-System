"""
Auth blueprint — demo-only. There's no real user database or session
system yet: this just validates the login form's fields and echoes
back what the frontend already stored in sessionStorage. Swap this for
real authentication (password hashing, sessions/JWT) before going live.
"""

from flask import Blueprint, request, jsonify

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    role = data.get("role")

    if not name or role not in ("student", "driver", "admin"):
        return jsonify({"error": "name and a valid role are required"}), 400

    # No password check, no session token issued — demo only.
    return jsonify({"status": "ok", "name": name, "role": role})
