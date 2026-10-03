# Smart Bus Tracker

Live GPS tracking for college and school buses. Students see the bus move on a map in real time with an ETA; drivers share their live location from a browser; admins manage routes, buses, and stops.

## Architecture

```
Smart-Bus-Tracker/
├── backend/
│   ├── app.py                # Entry point — registers all blueprints
│   ├── config.py              # DB credentials and app constants
│   ├── database/
│   │   ├── db.py              # Raw SQL — connection pool + queries
│   │   └── schema.sql         # Full schema + sample data
│   ├── routes/                # Flask blueprints (HTTP layer only)
│   │   ├── auth.py            # Demo login
│   │   ├── student.py         # GET /api/bus-location
│   │   ├── driver.py          # POST update-location, toggle-direction
│   │   ├── buses.py           # Bus list/register
│   │   ├── routes.py          # Route/stop CRUD + Dijkstra demo endpoint
│   │   └── tracking.py        # Fleet-wide position query (scaffolded)
│   ├── algorithms/            # Pure logic, no Flask/DB imports
│   │   ├── graph.py           # RouteGraph built from real stop data
│   │   ├── dijkstra.py        # Standalone shortest-path algorithm
│   │   └── eta.py             # Haversine distance + reached/next logic
│   ├── services/               # Business logic between routes/ and database/
│   │   ├── location_service.py
│   │   ├── trip_service.py
│   │   └── eta_service.py
│   ├── ml/                    # Future-stage ETA prediction (synopsis §5.8-5.9)
│   │   ├── train.py
│   │   └── predict.py
│   └── data/
│       └── trips.csv          # Sample trip history for ML training
└── frontend/
    ├── index.html              # Landing page
    ├── pages/                  # login, student, driver, admin
    ├── css/
    └── js/
```

Each layer only talks to the one below it: `routes/` calls `services/`, `services/` calls `database/` and `algorithms/`. Nothing in `algorithms/` or `database/` imports Flask.

## Setup

1. **Database**
   ```bash
   mysql -u root -p < backend/database/schema.sql
   ```
   This creates the database, tables, sample stops, and a return-direction route.

2. **Backend config**
   Edit `backend/config.py` and replace `"your_password"` with your actual MySQL password.

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the backend**
   ```bash
   cd backend
   python app.py
   ```
   Should print `Running on http://127.0.0.1:5000`.

5. **Run the frontend**
   Open `frontend/index.html` with VS Code's Live Server extension (or any static file server — opening it directly as a `file://` URL will break geolocation and API requests).

## API reference

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/auth/login` | Demo login (no real auth yet) |
| GET | `/api/bus-location?bus_id=` | Current position, stops, ETA for a bus |
| POST | `/api/update-location` | Driver pushes a GPS point |
| POST | `/api/buses/<id>/toggle-direction` | Flip a bus to its route's return direction |
| GET / POST | `/api/buses` | List / register buses |
| GET / POST | `/api/routes` | List / create routes |
| GET | `/api/routes/<id>/stops` | Stops for a route |
| POST | `/api/stops` | Add a stop to a route |
| GET | `/api/routes/<id>/shortest-path?from=&to=` | Dijkstra demo between two stops |
| GET | `/api/tracking/all` | Current position of every bus (not yet used by the frontend) |

## ML-based ETA (future stage)

`backend/data/trips.csv` holds sample trip history. Train a baseline model with:
```bash
cd backend
python ml/train.py
```
This saves `backend/ml/eta_model.joblib`. Once trained, wire `ml/predict.py`'s `predict_travel_time_min()` into `services/eta_service.py` in place of the plain distance/speed formula. Needs real logged trips (not the synthetic sample rows) to be meaningfully accurate.

## Design/launch rules for this project

No purple gradients, no pill-shaped buttons, no fake reviews/metrics/customer counters, no vague hero text, no emoji icons, no em dashes in UI copy, no over-the-top scroll animation, no AI-slop photos/copy, no cursor animation. Before launch: custom domain, favicon, remove any "made with AI" tag, and add privacy policy + terms and conditions pages.
