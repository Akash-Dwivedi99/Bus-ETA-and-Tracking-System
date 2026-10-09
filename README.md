# Campus Transit

A Flask and MySQL campus bus tracker. Students can view buses, route stops, and estimated arrivals. Drivers can share GPS while a trip is active and switch route direction. Admin pages manage buses, routes, and stops.

The sign-in page is a demo role selector. It does not create accounts or authenticate users. Keep this project on localhost or a controlled development network until real authentication and authorization are implemented.

## Requirements

- Python 3.11 or later
- MySQL 8
- A browser with JavaScript enabled

## Step 1: Initialize MySQL

In MySQL Workbench, run `backend/database/schema.sql` once. It creates the `bus_tracker` database, tables, and an illustrative sample route and bus. Replace the sample with authorized campus data before using it with riders. Do not rerun the seed script on an existing database because it inserts the sample records again.

Create the local app account in Workbench. Choose a local password, then use that same value in `.env`:

```sql
CREATE USER 'bus_tracker_app'@'localhost' IDENTIFIED BY 'CHOOSE_A_LOCAL_PASSWORD';
GRANT SELECT, INSERT, UPDATE, DELETE ON bus_tracker.* TO 'bus_tracker_app'@'localhost';
FLUSH PRIVILEGES;
```

## Step 2: Configure the app

Run these commands from the project root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
notepad .env
```

Set `BUS_DB_PASSWORD` in `.env` to the password you chose for `bus_tracker_app`. Keep `.env` private and do not commit it.

## Step 3: Run Flask

```powershell
python -m backend.app
```

Keep that terminal open and visit `http://127.0.0.1:5000`. This is the recommended local URL. VS Code Live Server also works when it opens the site on `localhost` or `127.0.0.1` port 5500 or 5501; the frontend then calls Flask on port 5000. Cross-origin access is limited to those local origins in development. If Live Server chooses another port, use the Flask URL directly.

Select **Student**, enter a display name, and continue. Choose a bus on the student page. The demo login does not check a password. The driver page requires browser location permission while a trip is active. Browser geolocation requires localhost or HTTPS.

## Troubleshooting

In a second PowerShell window, while Flask is running, check MySQL readiness and bus records:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/readyz"
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/buses"
```

`/readyz` should return `status: ready`. `/api/buses` should return a JSON list. If either returns 503, check that MySQL is running and that the host, port, user, password, and database in `.env` match MySQL. Restart Flask after changing `.env`.

## API overview

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/api/auth/login` | Validate demo name and role |
| GET | `/api/buses` | List buses and route names |
| GET | `/api/routes` | List routes |
| GET | `/api/bus-location?bus_id=...` | Get latest location, route stops, and ETA |
| POST | `/api/bus-location` | Store a driver location update |
| POST | `/api/buses/<id>/toggle-direction` | Switch a bus to its paired route |
| GET | `/healthz` | Check Flask process status |
| GET | `/readyz` | Check MySQL connection |

## Tests and checks

```powershell
python -m unittest discover -s tests -v
node --check frontend/js/api.js
node --check frontend/js/auth.js
node --check frontend/js/student.js
node --check frontend/js/driver.js
```

The unit tests mock database access. A successful live check still requires a running MySQL server with the schema loaded.

## Privacy and launch readiness

The driver page sends GPS coordinates to MySQL during an active trip. The student page uses browser geolocation locally to calculate distance from the bus. Define retention, access, consent, and operator contact details before real-world use. The privacy and terms pages are drafts and need review for the actual institution and jurisdiction. A custom domain, HTTPS, real user authentication, authorization, backups, and security review are not configured by this local project.
