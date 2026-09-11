"""
ML AQI Predictor Module.
Loads the trained model pipeline, formats tabular inputs, imputes missing features,
and computes factor contributions for agent explainability.
Supports both predict_aqi(data) and predict_aqi(model, data).
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import joblib
import numpy as np
import pandas as pd
from src.aqi_utils import get_aqi_category, get_aqi_status, identify_dominant_pollutant, get_health_message

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PRIMARY_MODEL_PATH = PROJECT_ROOT / "models" / "best_model.pkl"
FALLBACK_MODEL_PATH = PROJECT_ROOT / "models" / "linear_regression_model.pkl"

FEATURE_ORDER = [
    "PM2.5", "PM10", "NO", "NO2", "NOx", "NH3",
    "CO", "SO2", "O3", "Benzene", "Toluene", "Xylene",
    "Year", "Month", "Day"
]

# Baseline historical medians for Indian cities when specific trace gases are not measured
POLLUTANT_DEFAULTS = {
    "PM2.5": 65.0,
    "PM10": 110.0,
    "NO": 15.0,
    "NO2": 25.0,
    "NOx": 30.0,
    "NH3": 20.0,
    "CO": 1.1,
    "SO2": 12.0,
    "O3": 35.0,
    "Benzene": 2.5,
    "Toluene": 6.0,
    "Xylene": 2.0
}

_CACHED_MODEL = None


import logging

logger = logging.getLogger(__name__)


def load_model():
    """Load the trained AQI prediction model with fallback support and logging."""
    global _CACHED_MODEL
    if _CACHED_MODEL is not None:
        return _CACHED_MODEL

    candidate_models = [
        ("Primary Random Forest Model", PRIMARY_MODEL_PATH),
        ("Alternative Random Forest Model", PROJECT_ROOT / "models" / "random_forest_model.pkl"),
        ("Fallback Linear Regression Model", FALLBACK_MODEL_PATH)
    ]

    last_error = None
    for name, model_path in candidate_models:
        if model_path.exists():
            try:
                _CACHED_MODEL = joblib.load(model_path)
                logger.info("Successfully loaded %s from %s", name, model_path)
                return _CACHED_MODEL
            except Exception as e:
                logger.warning(
                    "Failed to deserialize %s at %s: %s. Attempting fallback.",
                    name, model_path, str(e)
                )
                last_error = e

    error_msg = f"No model artifact could be loaded from candidate paths. Last error: {last_error}"
    logger.error(error_msg)
    raise FileNotFoundError(error_msg)


def prepare_input(data: Union[Dict[str, Any], pd.DataFrame]) -> pd.DataFrame:
    """
    Prepare input data into the exact format and order expected by the ML model.
    Fills unspecified pollutants with sensible national baseline defaults.
    """
    if isinstance(data, pd.DataFrame):
        df_copy = data.copy()
        for feature in FEATURE_ORDER:
            if feature not in df_copy.columns:
                df_copy[feature] = POLLUTANT_DEFAULTS.get(feature, 0.0)
            else:
                df_copy[feature] = df_copy[feature].fillna(POLLUTANT_DEFAULTS.get(feature, 0.0))
        return df_copy[FEATURE_ORDER]

    now = datetime.now()
    prepared = {}

    for feature in FEATURE_ORDER:
        if feature in data and data[feature] is not None:
            try:
                prepared[feature] = float(data[feature])
            except (ValueError, TypeError):
                prepared[feature] = POLLUTANT_DEFAULTS.get(feature, 0.0)
        elif feature == "Year":
            prepared[feature] = float(data.get("Year", now.year))
        elif feature == "Month":
            prepared[feature] = float(data.get("Month", now.month))
        elif feature == "Day":
            prepared[feature] = float(data.get("Day", now.day))
        else:
            prepared[feature] = POLLUTANT_DEFAULTS.get(feature, 0.0)

    input_df = pd.DataFrame([prepared])
    return input_df[FEATURE_ORDER]


def predict_aqi(model_or_data: Any, input_data: Optional[Any] = None) -> float:
    """
    Predict AQI using the trained model.
    Supports both signatures:
      - predict_aqi(data)
      - predict_aqi(model, data)
    """
    if input_data is None:
        model = load_model()
        raw_data = model_or_data
    else:
        model = model_or_data
        raw_data = input_data

    input_df = prepare_input(raw_data)
    prediction = model.predict(input_df)
    return float(prediction[0])


def predict_aqi_rich(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predict AQI and return a structured analysis payload for the AI Agent.
    Includes AQI, category, confidence/model details, and major factor contributions.
    """
    model = load_model()
    input_df = prepare_input(data)
    prediction = float(model.predict(input_df)[0])
    prediction = max(0.0, round(prediction, 1))

    status = get_aqi_status(prediction)

    # Estimate major contributing factors
    input_pollutants = {
        col: float(input_df[col].iloc[0])
        for col in ["PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]
        if col in input_df.columns
    }
    dominant_analysis = identify_dominant_pollutant(input_pollutants)

    factors: List[Dict[str, Any]] = []
    for pol, ratio in dominant_analysis.get("all_ratios", {}).items():
        impact = "Critical" if ratio > 2.0 else "High" if ratio > 1.0 else "Moderate" if ratio > 0.5 else "Low"
        factors.append({
            "pollutant": pol,
            "measured_value": input_pollutants.get(pol, 0.0),
            "ratio_to_safe_limit": ratio,
            "impact_level": impact
        })

    factors = sorted(factors, key=lambda x: x["ratio_to_safe_limit"], reverse=True)

    is_pipeline = hasattr(model, "named_steps")
    model_info = {
        "model_architecture": "Random Forest Regressor" if not is_pipeline else "Random Forest Pipeline",
        "features_used": FEATURE_ORDER,
        "input_features_count": len(FEATURE_ORDER),
        "r2_score_benchmark": 0.8877,
        "mae_benchmark": 20.22
    }

    return {
        "aqi": prediction,
        "category": status["category"],
        "color": status["color"],
        "health_message": status["message"],
        "confidence_or_model_information": model_info,
        "dominant_pollutant": dominant_analysis["dominant"],
        "major_factors": factors[:4]
    }


def get_health_advice(aqi: float) -> str:
    """Return health advice based on AQI (Backwards compatibility)."""
    return get_health_message(aqi)


__all__ = [
    "load_model",
    "prepare_input",
    "predict_aqi",
    "predict_aqi_rich",
    "get_aqi_category",
    "get_health_advice",
    "get_health_message",
    "get_aqi_status"
]
