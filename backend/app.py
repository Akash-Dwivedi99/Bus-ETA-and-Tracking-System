"""
Smart Bus Tracker — Flask Backend entry point.

All the actual logic lives in routes/ (Flask blueprints), services/
(business logic + DB orchestration), algorithms/ (Dijkstra, graph, ETA
math) and database/ (raw SQL). This file just wires it all together.

Run:
  pip install -r requirements.txt
  python app.py
"""

from flask import Flask
from flask_cors import CORS

from backend.config import DEBUG, PORT
from backend.routes.auth import auth_bp
from backend.routes.student import student_bp
from backend.routes.driver import driver_bp
from backend.routes.buses import buses_bp
from backend.routes.routes import routes_bp
from backend.routes.tracking import tracking_bp

app = Flask(__name__)
CORS(app)  # allow the dashboard (served from a different origin/port) to call this API

app.register_blueprint(auth_bp)
app.register_blueprint(student_bp)
app.register_blueprint(driver_bp)
app.register_blueprint(buses_bp)
app.register_blueprint(routes_bp)
app.register_blueprint(tracking_bp)


if __name__ == "__main__":
    app.run(debug=DEBUG, port=PORT)
