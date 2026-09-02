"""
Unit & Integration Tests for Agent Tools.
Tests live air quality, weather forecasts, ML predictions, historical queries, and health guidance.
"""

from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.tools.health_knowledge_tool import get_aqi_health_guidance
from src.tools.historical_tool import get_historical_aqi
from src.tools.live_aqi_tool import fetch_live_air_quality, geocode_location
from src.tools.prediction_tool import predict_aqi_tool
from src.tools.weather_tool import evaluate_dispersion, fetch_weather_forecast


class TestAgentTools(unittest.TestCase):

    def test_geocode_known_city(self):
        geo = geocode_location("Kanpur")
        self.assertIsNotNone(geo)
        name, lat, lon = geo
        self.assertAlmostEqual(lat, 26.45, delta=0.2)
        self.assertAlmostEqual(lon, 80.33, delta=0.2)

    def test_live_aqi_tool_success(self):
        res = fetch_live_air_quality("Kanpur")
        self.assertEqual(res["status"], "success")
        self.assertIn("aqi", res)
        self.assertIn("category", res)
        self.assertIn("pollutants", res)
        self.assertIn("dominant_pollutant", res)
        self.assertGreaterEqual(res["aqi"], 0)

    def test_live_aqi_tool_invalid_location(self):
        res = fetch_live_air_quality("NonExistentCityXYZ12345")
        self.assertEqual(res["status"], "error")
        self.assertIn("message", res)

    def test_weather_tool_success(self):
        res = fetch_weather_forecast("Delhi")
        self.assertEqual(res["status"], "success")
        self.assertIn("temperature_c", res)
        self.assertIn("wind_speed_kmh", res)
        self.assertIn("dispersion_analysis", res)
        self.assertIn("pollution_trapping_risk", res["dispersion_analysis"])

    def test_weather_dispersion_logic(self):
        # Calm wind + high humidity should flag high risk
        stagnant = evaluate_dispersion(wind_speed=3.0, humidity=88.0, precip=0.0)
        self.assertEqual(stagnant["pollution_trapping_risk"], "High")

        # Rain should flag scrubbing effect
        rainy = evaluate_dispersion(wind_speed=12.0, humidity=90.0, precip=15.0)
        self.assertEqual(rainy["pollution_trapping_risk"], "Low")

    def test_prediction_tool_with_location(self):
        res = predict_aqi_tool(location="Delhi", target_date="tomorrow")
        self.assertEqual(res["status"], "success")
        self.assertIn("aqi", res)
        self.assertIn("category", res)
        self.assertIn("major_factors", res)

    def test_historical_tool_success(self):
        res = get_historical_aqi("Delhi", current_aqi=150.0)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["matched_historical_dataset"], "Delhi")
        self.assertIn("stats", res)
        self.assertIn("mean_aqi", res["stats"])
        self.assertIn("seasonal_averages", res)
        self.assertIsNotNone(res["comparison_with_current"])

    def test_historical_tool_regional_proxy(self):
        # Kanpur is proxied to Lucknow
        res = get_historical_aqi("Kanpur", current_aqi=75.0)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["matched_historical_dataset"], "Lucknow")
        self.assertTrue(res["is_regional_proxy"])

    def test_health_knowledge_tool(self):
        # Test clean conditions
        good_res = get_aqi_health_guidance(aqi=45.0, activity="running")
        self.assertEqual(good_res["status"], "success")
        self.assertEqual(good_res["category"], "Good")
        self.assertTrue(good_res["advisory"]["is_safe_for_exercise"])

        # Test severe conditions with asthma
        severe_res = get_aqi_health_guidance(aqi=380.0, condition="asthma", activity="running")
        self.assertFalse(severe_res["advisory"]["is_safe_for_exercise"])
        self.assertTrue(severe_res["advisory"]["mask_recommended"])
        self.assertIn("asthma", severe_res["advisory"]["condition_advice"].lower())


if __name__ == "__main__":
    unittest.main()
