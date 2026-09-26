"""
Unit tests for the Flask Application and Render deployment endpoints.
Tests normal functionality, edge cases, negative numbers, non-numeric strings, and error handling.
"""

from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from app import app
from flask import Flask


class TestFlaskRenderApp(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_flask_instance(self):
        """Verify the main entry file exports a valid Flask instance named 'app'."""
        self.assertIsInstance(app, Flask)

    def test_index_route(self):
        """Verify root route strictly serves the compiled React SPA and NOT the legacy Flask HTML."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<div id="root"></div>', response.data)
        self.assertIn(b"AirSense", response.data)
        self.assertNotIn(b'id="predictForm"', response.data)

    def test_react_static_assets_and_spa_fallback(self):
        """Verify compiled JS/CSS assets under /assets/ and SPA route fallback work."""
        index_html = self.client.get("/").get_data(as_text=True)
        import re
        js_match = re.search(r'src="(/assets/[^"]+\.js)"', index_html)
        self.assertIsNotNone(js_match, "Compiled JS bundle script tag must be present in index.html")
        asset_resp = self.client.get(js_match.group(1))
        self.assertEqual(asset_resp.status_code, 200)
        self.assertGreater(len(asset_resp.data), 1000)

        # Verify SPA client-side route fallback
        spa_resp = self.client.get("/dashboard")
        self.assertEqual(spa_resp.status_code, 200)
        self.assertIn(b'<div id="root"></div>', spa_resp.data)

    def test_health_route(self):
        """Verify health check returns healthy status with HTTP 200."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data["status"], "healthy")
        self.assertTrue(json_data["model_loaded"])

    def test_status_route_alias(self):
        """Verify status route alias works."""
        response = self.client.get("/status")
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data["status"], "healthy")

    def test_predict_endpoint_post_success(self):
        """Verify /predict endpoint returns predicted AQI for given values."""
        payload = {
            "location": "Delhi",
            "PM2.5": 75.0,
            "PM10": 115.0
        }
        response = self.client.post("/predict", json=payload)
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn("aqi", json_data)
        self.assertIn("category", json_data)
        self.assertGreater(json_data["aqi"], 0)

    def test_predict_endpoint_zero_values(self):
        """Verify zero pollutant concentrations are accepted as valid non-negative numbers."""
        payload = {
            "location": "Delhi",
            "PM2.5": 0.0,
            "PM10": 0.0
        }
        response = self.client.post("/predict", json=payload)
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn("aqi", json_data)

    def test_predict_endpoint_empty_fields(self):
        """Verify empty string fields (from form submit) are handled gracefully without 500 error."""
        payload = {
            "location": "Delhi",
            "PM2.5": "",
            "PM10": ""
        }
        response = self.client.post("/predict", json=payload)
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn("aqi", json_data)

    def test_predict_endpoint_string_input_validation_error(self):
        """Verify non-numeric string values return descriptive 400 error instead of 500 server crash."""
        payload = {
            "location": "Delhi",
            "PM2.5": "invalid_string",
            "PM10": 95.0
        }
        response = self.client.post("/predict", json=payload)
        self.assertEqual(response.status_code, 400)
        json_data = response.get_json()
        self.assertEqual(json_data["status"], "error")
        self.assertIn("expected a numeric value", json_data["message"])

    def test_predict_endpoint_negative_input_validation_error(self):
        """Verify negative concentrations return descriptive 400 error instead of 500."""
        payload = {
            "location": "Delhi",
            "PM2.5": -50.0,
            "PM10": 95.0
        }
        response = self.client.post("/predict", json=payload)
        self.assertEqual(response.status_code, 400)
        json_data = response.get_json()
        self.assertEqual(json_data["status"], "error")
        self.assertIn("cannot be negative", json_data["message"])

    def test_predict_endpoint_invalid_date_format(self):
        """Verify malformed target_date returns descriptive 400 error."""
        payload = {
            "location": "Delhi",
            "target_date": "invalid-date-format"
        }
        response = self.client.post("/predict", json=payload)
        self.assertEqual(response.status_code, 400)
        json_data = response.get_json()
        self.assertEqual(json_data["status"], "error")
        self.assertIn("Invalid date", json_data["message"])

    def test_agent_endpoint(self):
        """Verify /agent endpoint returns agent reasoning and natural language answer."""
        response = self.client.post("/agent", json={"query": "What is the AQI in Kanpur right now?"})
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data["status"], "success")
        self.assertIn("response", json_data)
        self.assertIn("activity", json_data)

    def test_historical_endpoint(self):
        """Verify /historical endpoint returns historical distributions and stats for a city."""
        response = self.client.get("/historical?city=Delhi")
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data["status"], "success")
        self.assertIn("stats", json_data)
        self.assertIn("mean_aqi", json_data["stats"])

    def test_cors_headers(self):
        """Verify CORS headers are present on responses."""
        response = self.client.get("/health")
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "*")
        self.assertIn("POST", response.headers.get("Access-Control-Allow-Methods", ""))

    def test_options_preflight(self):
        """Verify preflight OPTIONS request returns HTTP 200 and allowed CORS headers."""
        response = self.client.open("/predict", method="OPTIONS")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "*")
        self.assertIn("Content-Type", response.headers.get("Access-Control-Allow-Headers", ""))


    def test_live_invalid_coordinates(self):
        """Verify /live rejects out-of-range or malformed lat/lon coordinates with HTTP 400."""
        resp_range = self.client.get("/live?lat=999&lon=80.33")
        self.assertEqual(resp_range.status_code, 400)
        self.assertEqual(resp_range.get_json()["status"], "error")

        resp_missing = self.client.get("/live?lat=26.4499")
        self.assertEqual(resp_missing.status_code, 400)

        resp_nan = self.client.get("/live?lat=invalid&lon=80.33")
        self.assertEqual(resp_nan.status_code, 400)

    def test_live_with_coordinates(self):
        """Verify /live accepts lat/lon coordinates and returns normalized live contract."""
        from unittest.mock import patch
        mock_live = {
            "status": "success",
            "data_mode": "live",
            "location": "Kanpur, India",
            "latitude": 26.4499,
            "longitude": 80.3319,
            "aqi": 94.0,
            "category": "Satisfactory",
            "color": "#a3c853",
            "health_message": "Air quality is acceptable.",
            "dominant_pollutant": "PM2.5",
            "dominant_ratio": 0.9,
            "pollutants": {"PM2.5": 32.1, "PM10": 68.4, "NO2": 18.2, "SO2": 7.5, "CO": 0.55, "O3": 41.0},
            "measurement_time": "2026-09-25T14:00",
            "data_timestamp": "2026-09-25T14:00",
            "source": "Live Air Quality Data (Open-Meteo)",
        }
        mock_weather = {
            "status": "success",
            "temperature_c": 31.4,
            "feels_like_c": 34.0,
            "relative_humidity_pct": 58,
            "wind_speed_kmh": 11.2,
            "weather_condition": "Mainly clear",
            "dispersion_analysis": {"condition": "Favorable Dispersion"},
        }
        with patch("app.fetch_live_air_quality", return_value=mock_live), patch(
            "app.fetch_weather_forecast", return_value=mock_weather
        ):
            response = self.client.get("/live?lat=26.4499&lon=80.3319")
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertEqual(data["status"], "success")
            self.assertEqual(data["data_mode"], "live")
            self.assertEqual(data["location"], "Kanpur, India")
            self.assertEqual(data["latitude"], 26.4499)
            self.assertEqual(data["longitude"], 80.3319)
            self.assertIn("weather", data)
            self.assertEqual(data["weather"]["temperature"], 31.4)


if __name__ == "__main__":
    unittest.main()


