"""
ML AQI Prediction Tool.
Provides an agent-callable tool interface over the trained Scikit-learn Random Forest model.
Supports standalone feature payloads as well as location-aware automatic feature fetching.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

# Defensive import: handles both direct and package imports
try:
    from src.predictor import predict_aqi_rich
except (ImportError, AttributeError):
    try:
        from predictor import predict_aqi_rich
    except (ImportError, AttributeError):
        # Fallback to local rich implementation using existing predict_aqi
        try:
            from src.predictor import predict_aqi, load_model
        except ImportError:
            from predictor import predict_aqi, load_model
        try:
            from src.aqi_utils import get_aqi_status, identify_dominant_pollutant
        except ImportError:
            from aqi_utils import get_aqi_status, identify_dominant_pollutant

        def predict_aqi_rich(data: Dict[str, Any]) -> Dict[str, Any]:
            model = load_model()
            pred = predict_aqi(model, data)
            status = get_aqi_status(pred)
            return {
                "aqi": round(pred, 1),
                "category": status["category"],
                "color": status.get("color", "#FFCC00"),
                "health_message": status.get("message", ""),
                "confidence_or_model_information": {"model": "Random Forest Regressor"},
                "dominant_pollutant": "PM2.5",
                "major_factors": []
            }

try:
    from src.tools.live_aqi_tool import fetch_live_air_quality
except ImportError:
    from tools.live_aqi_tool import fetch_live_air_quality


def predict_aqi_tool(
    input_data: Optional[Dict[str, Any]] = None,
    location: Optional[str] = None,
    target_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Predict AQI using the trained Machine Learning pipeline.
    
    Parameters:
      input_data: Optional dictionary containing pollutant features (PM2.5, PM10, NO2, etc.).
      location: Optional location name. If provided and input_data is incomplete,
                live pollutant baselines will be retrieved for this location.
      target_date: Optional target date string ('YYYY-MM-DD' or 'tomorrow').
    """
    payload: Dict[str, Any] = {}
    if input_data:
        payload.update(input_data)

    # Determine date features
    now = datetime.now()
    if target_date:
        t_lower = target_date.lower().strip()
        if t_lower == "tomorrow":
            target_dt = now + timedelta(days=1)
        elif t_lower == "today":
            target_dt = now
        else:
            try:
                target_dt = datetime.strptime(target_date, "%Y-%m-%d")
            except ValueError:
                target_dt = now + timedelta(days=1)
    else:
        target_dt = now

    payload["Year"] = target_dt.year
    payload["Month"] = target_dt.month
    payload["Day"] = target_dt.day

    # If location is provided and key pollutants are missing, hydrate with live baselines
    used_live_baseline = False
    if location and (not input_data or ("PM2.5" not in input_data and "pm25" not in input_data)):
        live_res = fetch_live_air_quality(location)
        if live_res.get("status") == "success":
            used_live_baseline = True
            live_pols = live_res.get("pollutants", {})
            for k, v in live_pols.items():
                if v is not None and k not in payload:
                    payload[k] = v

    try:
        rich_pred = predict_aqi_rich(payload)
        rich_pred["status"] = "success"
        rich_pred["target_date"] = target_dt.strftime("%Y-%m-%d")
        rich_pred["location_context"] = location or "Generic Profile"
        rich_pred["used_live_station_baseline"] = used_live_baseline
        return rich_pred

    except Exception as e:
        return {
            "status": "error",
            "message": f"ML Model prediction failed: {str(e)}",
            "location_context": location
        }
