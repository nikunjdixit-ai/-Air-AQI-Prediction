"""
Unit tests for the Flask Application and Render deployment endpoints.
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
        """Verify root route returns HTTP 200."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Air Quality Intelligence", response.data)

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

    def test_predict_endpoint_post(self):
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

    def test_agent_endpoint(self):
        """Verify /agent endpoint returns agent reasoning and natural language answer."""
        response = self.client.post("/agent", json={"query": "What is the AQI in Kanpur right now?"})
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data["status"], "success")
        self.assertIn("response", json_data)
        self.assertIn("activity", json_data)


if __name__ == "__main__":
    unittest.main()
