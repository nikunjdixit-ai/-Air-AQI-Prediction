"""
Unit tests for the Machine Learning Prediction Engine.
Tests model loading, tabular preprocessing, scalar predictions, and rich factor breakdowns.
"""

from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.predictor import load_model, predict_aqi, predict_aqi_rich


class TestPrediction(unittest.TestCase):

    def setUp(self):
        self.sample_data = {
            "PM2.5": 80.0,
            "PM10": 120.0,
            "NO": 40.0,
            "NO2": 30.0,
            "NOx": 50.0,
            "NH3": 20.0,
            "CO": 1.0,
            "SO2": 20.0,
            "O3": 50.0,
            "Benzene": 2.0,
            "Toluene": 5.0,
            "Xylene": 1.0,
            "Year": 2026,
            "Month": 8,
            "Day": 2
        }

    def test_model_loading(self):
        model = load_model()
        self.assertIsNotNone(model)

    def test_scalar_prediction(self):
        pred = predict_aqi(self.sample_data)
        self.assertIsInstance(pred, float)
        self.assertGreater(pred, 0)
        self.assertLess(pred, 1000)

    def test_partial_features_handling(self):
        # Only provide PM2.5 and PM10
        partial = {"PM2.5": 95.0, "PM10": 150.0}
        pred = predict_aqi(partial)
        self.assertIsInstance(pred, float)
        self.assertGreater(pred, 0)

    def test_rich_prediction_payload(self):
        rich = predict_aqi_rich(self.sample_data)
        self.assertIn("aqi", rich)
        self.assertIn("category", rich)
        self.assertIn("confidence_or_model_information", rich)
        self.assertIn("major_factors", rich)
        self.assertIn("dominant_pollutant", rich)
        self.assertIsInstance(rich["major_factors"], list)


if __name__ == "__main__":
    unittest.main()
