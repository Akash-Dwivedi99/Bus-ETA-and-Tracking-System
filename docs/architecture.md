# Architecture

- Flask serves frontend files and JSON APIs from one origin.
- Route blueprints handle demo role selection, student bus views, driver trip controls, bus/route administration, and location tracking.
- Services coordinate ETA calculation and MySQL operations. Database helpers use a lazy connection pool so the frontend can render even before a database connection succeeds.
- MySQL stores routes, paired return routes, buses, stops, and timestamped GPS locations.
- The student page polls bus data every five seconds and animates marker movement between received positions. Route progress uses the configured reached-stop radius.
- The driver page requests browser geolocation during an active trip and sends location updates to the API. Route direction changes select the paired route.

The login page only validates a display name and selected role. It is a project demo, not account authentication or authorization. Keep administrative and driver endpoints on a controlled development environment until those protections are added.

`/healthz` checks that Flask is responding. `/readyz` performs a MySQL query and reports whether the database connection is ready.
