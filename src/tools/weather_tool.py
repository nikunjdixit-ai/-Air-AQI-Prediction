"""
Weather Tool.
Retrieves real-time weather and forecast conditions (temperature, humidity, wind speed, precipitation)
from the Open-Meteo Weather API and evaluates atmospheric dispersion indices.
"""

from typing import Any, Dict, Optional
import requests
from src.tools.live_aqi_tool import geocode_location

WMO_WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}


def evaluate_dispersion(wind_speed: float, humidity: float, precip: float) -> Dict[str, Any]:
    """
    Evaluate atmospheric ventilation/dispersion condition for air quality accumulation.
    Low wind (< 8 km/h) and high humidity (> 75%) promote particulate trapping and smog formation.
    Rain promotes particulate washout (wet deposition).
    """
    if precip > 1.0:
        condition = "Favorable (Scrubbing Effect)"
        risk = "Low"
        explanation = "Rainfall helps scrub and wash out particulate matter from the lower atmosphere."
    elif wind_speed < 6.0 and humidity > 75.0:
        condition = "Very Unfavorable (Stagnant / Inversion Risk)"
        risk = "High"
        explanation = "Calm winds and high humidity trap vehicular and industrial emissions close to ground level."
    elif wind_speed < 10.0:
        condition = "Moderate Dispersion"
        risk = "Moderate"
        explanation = "Mild breeze allows moderate pollutant accumulation during peak commute hours."
    else:
        condition = "Favorable Dispersion"
        risk = "Low"
        explanation = "Brisk winds facilitate rapid dilution and dispersion of airborne pollutants."

    return {
        "condition": condition,
        "pollution_trapping_risk": risk,
        "explanation": explanation
    }


# Calibrated seasonal weather baselines for major Indian cities when external live weather API is unreachable
CITY_WEATHER_BASELINES: Dict[str, Dict[str, Any]] = {
    "kanpur": {"temperature_c": 28.0, "feels_like_c": 30.0, "relative_humidity_pct": 64, "wind_speed_kmh": 8.4, "condition": "Partly cloudy"},
    "delhi": {"temperature_c": 31.0, "feels_like_c": 33.0, "relative_humidity_pct": 58, "wind_speed_kmh": 6.2, "condition": "Haze"},
    "mumbai": {"temperature_c": 30.0, "feels_like_c": 35.0, "relative_humidity_pct": 75, "wind_speed_kmh": 12.0, "condition": "Humid"},
    "bengaluru": {"temperature_c": 24.0, "feels_like_c": 24.0, "relative_humidity_pct": 60, "wind_speed_kmh": 10.0, "condition": "Mainly clear"},
    "bangalore": {"temperature_c": 24.0, "feels_like_c": 24.0, "relative_humidity_pct": 60, "wind_speed_kmh": 10.0, "condition": "Mainly clear"},
    "lucknow": {"temperature_c": 29.0, "feels_like_c": 31.0, "relative_humidity_pct": 61, "wind_speed_kmh": 7.5, "condition": "Partly cloudy"},
    "kolkata": {"temperature_c": 30.0, "feels_like_c": 34.0, "relative_humidity_pct": 72, "wind_speed_kmh": 9.0, "condition": "Hazy"},
    "chennai": {"temperature_c": 32.0, "feels_like_c": 37.0, "relative_humidity_pct": 78, "wind_speed_kmh": 11.0, "condition": "Humid"},
}


def get_fallback_weather(
    location_name: str,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    reason: str = "Provider unavailable",
) -> Dict[str, Any]:
    """
    Provide calibrated city baseline or seasonal average explicitly tagged as non-live.
    Ensures graceful degradation without presenting fallback estimates as live telemetry.
    """
    city_key = None
    if location_name:
        clean = location_name.split(",")[0].strip().lower()
        if clean in CITY_WEATHER_BASELINES:
            city_key = clean

    base = CITY_WEATHER_BASELINES.get(
        city_key,
        {
            "temperature_c": 28.0,
            "feels_like_c": 30.0,
            "relative_humidity_pct": 65,
            "wind_speed_kmh": 8.0,
            "condition": "Partly cloudy",
        },
    )

    dispersion = evaluate_dispersion(
        base["wind_speed_kmh"], float(base["relative_humidity_pct"]), 0.0
    )

    return {
        "status": "success",
        "data_mode": "offline_baseline",
        "location": location_name,
        "latitude": lat,
        "longitude": lon,
        "temperature_c": base["temperature_c"],
        "feels_like_c": base["feels_like_c"],
        "relative_humidity_pct": base["relative_humidity_pct"],
        "wind_speed_kmh": base["wind_speed_kmh"],
        "wind_direction_deg": 180,
        "precipitation_mm": 0.0,
        "weather_condition": base["condition"],
        "dispersion_analysis": dispersion,
        "forecast": [],
        "source": f"Seasonal Baseline Fallback ({reason})",
    }


from src.tools.live_aqi_tool import geocode_location, reverse_geocode_coordinates


def fetch_weather_forecast(
    location: Optional[str] = None,
    date_or_time: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Retrieve current weather and 3-day forecast for a given location or coordinates.
    Includes temperature, humidity, wind velocity, precipitation, and atmospheric dispersion index.
    """
    if latitude is not None and longitude is not None:
        lat = float(latitude)
        lon = float(longitude)
        resolved_name = (
            location.strip()
            if (location and location.strip())
            else reverse_geocode_coordinates(lat, lon)
        )
    else:
        target_loc = location or "Delhi"
        geo = geocode_location(target_loc)
        if not geo:
            return {
                "status": "error",
                "message": f"Could not geocode location '{target_loc}' for weather forecast.",
                "location": target_loc
            }
        resolved_name, lat, lon = geo

    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,wind_direction_10m"
            f"&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,wind_speed_10m_max"
            f"&timezone=auto"
        )
        resp = None
        for attempt in range(2):
            try:
                resp = requests.get(url, timeout=12)
                if resp.status_code == 200:
                    break
            except Exception:
                if attempt == 1:
                    raise

        if not resp or resp.status_code != 200:
            status_code = resp.status_code if resp else "unknown"
            return get_fallback_weather(resolved_name, lat, lon, reason=f"HTTP {status_code}")

        data = resp.json()
        current = data.get("current", {})
        daily = data.get("daily", {})

        temp = current.get("temperature_2m")
        feels_like = current.get("apparent_temperature")
        humidity = current.get("relative_humidity_2m")
        wind_speed = current.get("wind_speed_10m")
        wind_dir = current.get("wind_direction_10m")
        precip = current.get("precipitation", 0.0)
        code = current.get("weather_code", 0)
        weather_desc = WMO_WEATHER_CODES.get(code, "Clear to partly cloudy")

        dispersion = evaluate_dispersion(wind_speed or 0.0, humidity or 50.0, precip or 0.0)

        # Extract next 3 days forecast summary
        forecast_days = []
        if "time" in daily and len(daily["time"]) > 0:
            times = daily["time"][:3]
            t_max = daily.get("temperature_2m_max", [])
            t_min = daily.get("temperature_2m_min", [])
            precip_prob = daily.get("precipitation_probability_max", [])
            w_codes = daily.get("weather_code", [])

            for i in range(len(times)):
                forecast_days.append({
                    "date": times[i],
                    "condition": WMO_WEATHER_CODES.get(w_codes[i] if i < len(w_codes) else 0, "Clear"),
                    "temp_max_c": t_max[i] if i < len(t_max) else None,
                    "temp_min_c": t_min[i] if i < len(t_min) else None,
                    "precipitation_probability": f"{precip_prob[i]}%" if i < len(precip_prob) else "0%"
                })

        return {
            "status": "success",
            "data_mode": "live",
            "location": resolved_name,
            "latitude": lat,
            "longitude": lon,
            "temperature_c": temp,
            "feels_like_c": feels_like,
            "relative_humidity_pct": humidity,
            "wind_speed_kmh": wind_speed,
            "wind_direction_deg": wind_dir,
            "precipitation_mm": precip,
            "weather_condition": weather_desc,
            "dispersion_analysis": dispersion,
            "forecast": forecast_days,
            "source": "Open-Meteo Global Weather Service"
        }

    except Exception as e:
        return get_fallback_weather(resolved_name, lat, lon, reason=f"API error: {str(e)}")
