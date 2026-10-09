import unittest
from unittest.mock import patch

from backend.app import app


class BusApiTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_demo_login_accepts_canonical_and_compatibility_paths(self):
        for path in ("/api/auth/login", "/auth/login"):
            response = self.client.post(
                path, json={"name": "Test Student", "role": "student"}
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_json()["role"], "student")

    def test_demo_login_rejects_unknown_role(self):
        response = self.client.post(
            "/api/auth/login", json={"name": "Test", "role": "unknown"}
        )
        self.assertEqual(response.status_code, 400)

    @patch("backend.routes.buses.list_buses", return_value=[
        {"id": "bus-1", "bus_number": "Bus 01", "route_name": "Test Route"}
    ])
    def test_bus_list_returns_service_data(self, _list_buses):
        response = self.client.get("/api/buses")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()[0]["id"], "bus-1")

    def test_health_endpoint_sets_security_headers(self):
        response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
        self.assertIn("tile.openstreetmap.org", response.headers["Content-Security-Policy"])

    def test_local_live_server_preflight_is_allowed(self):
        response = self.client.options(
            "/api/auth/login",
            headers={
                "Origin": "http://127.0.0.1:5500",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Access-Control-Allow-Origin"], "http://127.0.0.1:5500")

    def test_non_local_origins_receive_no_cors_access(self):
        response = self.client.post(
            "/api/auth/login",
            json={"name": "Test Student", "role": "student"},
            headers={"Origin": "https://example.com"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Access-Control-Allow-Origin", response.headers)


if __name__ == "__main__":
    unittest.main()
