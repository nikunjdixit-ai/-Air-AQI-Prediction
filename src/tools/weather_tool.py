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


def fetch_weather_forecast(location: str, date_or_time: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve current weather and 3-day forecast for a given location.
    Includes temperature, humidity, wind velocity, precipitation, and atmospheric dispersion index.
    """
    geo = geocode_location(location)
    if not geo:
        return {
            "status": "error",
            "message": f"Could not geocode location '{location}' for weather forecast.",
            "location": location
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
        resp = requests.get(url, timeout=8)
        if resp.status_code != 200:
            return {
                "status": "error",
                "message": f"Weather API returned HTTP status {resp.status_code}",
                "location": resolved_name
            }

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
        return {
            "status": "error",
            "message": f"Network or parsing error fetching weather: {str(e)}",
            "location": resolved_name
        }
