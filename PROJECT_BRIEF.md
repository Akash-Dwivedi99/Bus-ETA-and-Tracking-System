# Smart Bus Tracker — Project Brief

Use this document as context when asking any AI tool (ChatGPT, Gemini, another Claude session, etc.) to contribute to this project. It describes what the project is, what's already built, and the conventions to follow.

## 1. What this is

A live GPS tracking system for college and school buses, similar in spirit to Uber/Rapido but scoped to a fixed-route campus bus. It is a BCA (AI & DS) mini-project submitted as a synopsis at Graphic Era (Deemed to be University), Dehradun.

Three user roles:
- **Student** — views the bus's live position on a map, gets an ETA to their stop, and sees how far the bus is from their own current location.
- **Driver** — opens a page on their phone, taps "Start Trip," and their live GPS is pushed to the server automatically. Can switch between a route's forward and return direction.
- **Admin** — manages routes, buses, and stops through a panel (no code changes needed to add a new bus or route).

## 2. Tech stack

- **Backend:** Python, Flask, MySQL (via `mysql-connector-python`)
- **Frontend:** Plain HTML/CSS/JavaScript (no framework, no build step) — Leaflet.js + OpenStreetMap for the map
- **Algorithms:** Dijkstra's algorithm over a graph of stops (nodes = stops, edges = Haversine distance between consecutive stops), used for shortest-path queries
- **Future stage:** ML-based ETA prediction (scikit-learn linear regression) trained on historical trip data, as a planned upgrade over the current formula-based ETA
- **Tooling:** Git/GitHub for version control, Postman for API testing

## 3. Architecture

```
Smart-Bus-Tracker/
├── backend/
│   ├── app.py                 # Entry point — registers Flask blueprints, nothing else
│   ├── config.py               # DB credentials + constants (AVG_SPEED_KMPH, REACHED_RADIUS_KM, etc.)
│   ├── database/
│   │   ├── db.py                # Connection pool + all raw SQL queries
│   │   └── schema.sql           # Full schema + sample seed data
│   ├── routes/                  # Flask blueprints — HTTP request/response only, no business logic
│   │   ├── auth.py               # Demo login (no real auth yet)
│   │   ├── student.py            # GET /api/bus-location
│   │   ├── driver.py             # POST update-location, toggle-direction
│   │   ├── buses.py              # GET/POST /api/buses
│   │   ├── routes.py             # Route/stop CRUD + Dijkstra demo endpoint
│   │   └── tracking.py           # GET /api/tracking/all (fleet-wide, scaffolded for later)
│   ├── algorithms/               # Pure functions — no Flask or DB imports
│   │   ├── graph.py               # RouteGraph, built from real stop data
│   │   ├── dijkstra.py            # Standalone shortest-path algorithm
│   │   └── eta.py                 # Haversine distance + reached/next-stop logic
│   ├── services/                 # Business logic between routes/ and database/
│   │   ├── location_service.py
│   │   ├── trip_service.py
│   │   └── eta_service.py
│   ├── ml/
│   │   ├── train.py               # Trains a baseline ETA regression model
│   │   └── predict.py             # Loads it (falls back to plain formula if untrained)
│   └── data/
│       └── trips.csv              # Sample historical trip data for ML training
└── frontend/
    ├── index.html                 # Landing page
    ├── pages/
    │   ├── login.html              # Role selection (student/driver/admin)
    │   ├── student.html            # Live map + ETA dashboard
    │   ├── driver.html             # Start/End Trip, direction switch
    │   └── admin.html              # Manage routes/buses/stops
    ├── css/                        # One shared style.css (design tokens) + one file per page
    └── js/
        ├── api.js                  # Shared fetch wrapper + demo session helpers
        ├── map.js                  # Shared Leaflet setup, icons, marker animation
        ├── auth.js, student.js, driver.js, admin.js   # One per page
```

**Layering rule:** `routes/` calls `services/`, `services/` calls `database/` and `algorithms/`. Nothing in `algorithms/` or `database/` imports Flask. Keep new backend code inside this layering — don't put SQL in a route file or Flask imports in `algorithms/`.

## 4. Database schema

Four tables: `routes` (id, name, `paired_route_id` linking a route to its opposite direction), `buses` (id, bus_number, route_id), `stops` (id, route_id, name, lat, lng, stop_order), `bus_locations` (id, bus_id, lat, lng, recorded_at — one row per GPS ping, never updated in place).

## 5. API reference

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/auth/login` | Demo login (name + role, no password) |
| GET | `/api/bus-location?bus_id=` | Current position, stop list with reached/next status, ETA |
| POST | `/api/update-location` | Driver pushes a GPS point (`bus_id`, `lat`, `lng`) |
| POST | `/api/buses/<id>/toggle-direction` | Flip a bus to its route's return direction |
| GET / POST | `/api/buses` | List / register buses |
| GET / POST | `/api/routes` | List / create routes |
| GET | `/api/routes/<id>/stops` | Stops for a route, in order |
| POST | `/api/stops` | Add a stop to a route |
| GET | `/api/routes/<id>/shortest-path?from=&to=` | Dijkstra demo between two named stops |
| GET | `/api/tracking/all` | Current position of every bus (not yet wired into any page) |

## 6. Key logic worth knowing before touching it

- **ETA / reached-stop logic** (`algorithms/eta.py`): anchored on whichever stop is currently *closest* to the bus, not a simple "within X meters" check — a naive proximity check breaks once the bus drives further than the radius away from a stop it already passed (the stop would wrongly become "next" again with a climbing ETA). If you touch this function, keep that anchoring behavior.
- **Bidirectional routes:** modeled as two separate `routes` rows (forward + return) linked via `paired_route_id`, with stops mirrored in reverse order — not a single route trying to work both directions.
- **Frontend polling:** the student dashboard polls `/api/bus-location` every 5 seconds and animates the marker between points (`animateMarkerTo` in `map.js`) rather than teleporting it, with a pulsing glow while in motion.
- **No real auth yet:** `routes/auth.py` and the frontend's login flow are both demo-only (`sessionStorage`, no password check, no session tokens). This is a known gap, not an oversight.

## 7. Design rules (frontend)

Dark "transit board" visual identity — ink-dark panels, amber as the single accent color for anything live, monospace numerals for data (JetBrains Mono + Space Grotesk, via Google Fonts). Hard constraints: **no purple gradients, no pill-shaped buttons, no fake reviews/metrics/customer counters, no vague hero text, no emoji icons (use inline SVG instead), no em dashes in UI copy, no over-the-top scroll animation, no AI-slop photos/copy, no cursor animation.** Before any public launch: custom domain, favicon, remove any "made with AI" tag, add privacy policy + terms and conditions pages.

## 8. Current status

**Working end-to-end:** database, backend (all endpoints above), student dashboard (live map, ETA, student's own location + distance-to-bus, bidirectional-route-aware), driver page (live GPS push, direction switch), admin page (manage routes/buses/stops), Dijkstra/graph module (standalone + demo endpoint).

**Not yet done / known gaps:**
- Real authentication (currently demo-only)
- ML-based ETA is scaffolded (`ml/train.py`, `ml/predict.py`, sample `trips.csv`) but not wired into `services/eta_service.py` — still uses the plain distance/speed formula. Needs real logged trip data to be worth enabling.
- `/api/tracking/all` (fleet-wide view) exists but no frontend page uses it yet — a natural fit for an admin live-map view.
- No automated tests.
- No deployment/hosting setup (runs locally: Flask dev server + VS Code Live Server).

## 9. What kind of contribution is useful right now

Pick one: wiring the ML model into the live ETA endpoint, building a fleet-overview map for the admin page using `/api/tracking/all`, adding real authentication, writing tests for `algorithms/eta.py` and `algorithms/dijkstra.py` (they're pure functions, easy to unit test), or a deployment guide. Keep new code inside the existing layering (section 3) and follow the design rules (section 7) for anything user-facing.
