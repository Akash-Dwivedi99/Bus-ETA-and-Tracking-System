# Security notes

## Current limitations

- The login screen is a demo role selector. It does not authenticate users or enforce student, driver, or admin authorization. Do not expose admin or driver APIs publicly until real authentication and per-role authorization are implemented.
- Driver GPS is written to the MySQL database during a trip. The project has no configurable retention or consent workflow. Define both before using real rider or driver data.
- Student browser location is used locally to calculate distance from the bus; it is not sent to the bus API by the student page.
- The example route and bus in the schema are illustrative. Replace them with authorized data.
- This project has not received an independent security audit. Privacy and terms pages are drafts requiring operator-specific review.

## Local operation

Keep `.env` private. Use a dedicated MySQL account limited to the `bus_tracker` database and the required read/write statements. The Flask server is available at `http://127.0.0.1:5000`. For local development only, the frontend also supports VS Code Live Server on loopback ports 5500 and 5501. Flask adds CORS headers only for those exact origins and only when `APP_ENV=development`.

The app sets restrictive response headers. It allows the external Leaflet CDN, Google Fonts, and OpenStreetMap tiles used by the pages. A network connection is required for those external map and font assets.

Do not use this demo role selector as a security boundary. Do not deploy publicly until authentication, authorization, HTTPS, backups, location consent/retention, and legal review are complete.
