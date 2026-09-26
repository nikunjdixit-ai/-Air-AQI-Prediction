"""
Live Air Quality Tool.
Retrieves real-time atmospheric pollutant concentrations and AQI from public APIs
(Open-Meteo Air Quality API / WAQI / OpenAQ) with geocoding and offline city coordinates.
"""

from datetime import datetime
import math
from typing import Any, Dict, Optional, Tuple
import requests
from src.aqi_utils import get_aqi_category, get_aqi_color, get_health_message, identify_dominant_pollutant

# Fallback coordinates for major Indian cities to ensure resilience against DNS/rate-limit issues
CITY_COORDINATES_CACHE: Dict[str, Tuple[float, float]] = {
    "kanpur": (26.4499, 80.3319),
    "delhi": (28.6139, 77.2090),
    "mumbai": (19.0760, 72.8777),
    "bengaluru": (12.9716, 77.5946),
    "bangalore": (12.9716, 77.5946),
    "kolkata": (22.5726, 88.3639),
    "chennai": (13.0827, 80.2707),
    "hyderabad": (17.3850, 78.4867),
    "ahmedabad": (23.0225, 72.5714),
    "lucknow": (26.8467, 80.9462),
    "patna": (25.5941, 85.1376),
    "jaipur": (26.9124, 75.7873),
    "pune": (18.5204, 73.8567),
    "chandigarh": (30.7333, 76.7794),
    "bhopal": (23.2599, 77.4126),
    "gurugram": (28.4595, 77.0266),
    "gurgaon": (28.4595, 77.0266),
    "noida": (28.5355, 77.3910),
    "amritsar": (31.6340, 74.8723),
    "varanasi": (25.3176, 82.9739),
    "agra": (27.1767, 78.0081)
}


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance in kilometers between two coordinates."""
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    return 2.0 * r * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))


def reverse_geocode_coordinates(lat: float, lon: float) -> str:
    """
    Resolve (latitude, longitude) into a human-readable city/region name.
    Checks local city coordinate cache first (within 40 km), then queries
    OpenStreetMap Nominatim reverse geocoding API with safe fallback.
    """
    best_city = None
    best_dist = float("inf")
    for city, (c_lat, c_lon) in CITY_COORDINATES_CACHE.items():
        if city in ("bangalore", "gurgaon"):
            continue
        dist = _haversine_km(lat, lon, c_lat, c_lon)
        if dist < best_dist:
            best_dist = dist
            best_city = city.title()

    if best_city and best_dist <= 40.0:
        return f"{best_city}, India"

    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=10&addressdetails=1"
        resp = requests.get(
            url,
            headers={"User-Agent": "AirSense-AQI-Monitor/1.1"},
            timeout=3
        )
        if resp.status_code == 200:
            data = resp.json()
            addr = data.get("address", {})
            place = (
                addr.get("city")
                or addr.get("town")
                or addr.get("municipality")
                or addr.get("state_district")
                or addr.get("county")
                or addr.get("state")
            )
            country = addr.get("country")
            if place and country:
                return f"{place}, {country}"
            if place:
                return str(place)
    except Exception:
        pass

    return f"{lat:.2f}°N, {lon:.2f}°E"


def geocode_location(location: str) -> Optional[Tuple[str, float, float]]:
    """
    Resolve a city or place name into (resolved_name, latitude, longitude).
    Checks fallback cache first, then calls Open-Meteo Geocoding API.
    """
    cleaned = location.strip().lower()

    # Check cache
    if cleaned in CITY_COORDINATES_CACHE:
        lat, lon = CITY_COORDINATES_CACHE[cleaned]
        return location.title(), lat, lon

    # Check partial match in cache
    for city, coords in CITY_COORDINATES_CACHE.items():
        if city in cleaned or cleaned in city:
            return city.title(), coords[0], coords[1]

    # Call Open-Meteo Geocoding API (free, no auth required)
    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={requests.utils.quote(location)}&count=1&language=en&format=json"
        resp = requests.get(url, timeout=6)
        if resp.status_code == 200:
            data = resp.json()
            if "results" in data and len(data["results"]) > 0:
                first = data["results"][0]
                return first["name"], float(first["latitude"]), float(first["longitude"])
    except Exception:
        pass

    return None


def fetch_live_air_quality(
    location: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Retrieve live air quality metrics for a specified city or geographic coordinates.
    
    Returns a structured dictionary with:
      - status: 'success' or 'error'
      - data_mode: 'live'
      - location: Resolved location name
      - latitude / longitude: Coordinates queried
      - aqi: Computed or measured AQI
      - category: AQI Category (Good, Satisfactory, Moderate, Poor, Very Poor, Severe)
      - dominant_pollutant: Primary contributing pollutant
      - pollutants: Detailed concentrations (PM2.5, PM10, NO2, SO2, CO, O3)
      - data_timestamp: ISO sensor timestamp
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
                "message": f"Could not find coordinates for location '{target_loc}'. Please check spelling or try a major nearby city.",
                "location": target_loc
            }
        resolved_name, lat, lon = geo

    try:
        # Query Open-Meteo Air Quality API with retry for transient network glitches
        aq_url = (
            f"https://air-quality-api.open-meteo.com/v1/air-quality"
            f"?latitude={lat}&longitude={lon}"
            f"&current=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,european_aqi,us_aqi"
        )
        resp = None
        for attempt in range(2):
            try:
                resp = requests.get(aq_url, timeout=12)
                if resp.status_code == 200:
                    break
            except Exception:
                if attempt == 1:
                    raise

        if not resp or resp.status_code != 200:
            status_code = resp.status_code if resp else "unknown"
            return {
                "status": "error",
                "message": f"Air Quality API returned HTTP status {status_code}",
                "location": resolved_name
            }

        data = resp.json()
        current = data.get("current", {})

        pm25 = current.get("pm2_5")
        pm10 = current.get("pm10")
        no2 = current.get("nitrogen_dioxide")
        so2 = current.get("sulphur_dioxide")
        co = current.get("carbon_monoxide")
        if co is not None:
            # Convert ug/m3 to mg/m3 for CO if needed (standard CO threshold is mg/m3)
            co_mg = round(co / 1000.0, 2)
        else:
            co_mg = None
        o3 = current.get("ozone")

        us_aqi = current.get("us_aqi")
        european_aqi = current.get("european_aqi")

        # Estimate Indian AQI using sub-index formula approximation based on PM2.5 / PM10 / US AQI
        # If US AQI is present, it aligns very closely with CPCB for particulate matter
        if us_aqi is not None:
            computed_aqi = float(us_aqi)
        elif pm25 is not None:
            # Simple Indian CPCB Sub-index approximation for PM2.5
            if pm25 <= 30:
                computed_aqi = pm25 * (50 / 30)
            elif pm25 <= 60:
                computed_aqi = 50 + (pm25 - 30) * (50 / 30)
            elif pm25 <= 90:
                computed_aqi = 100 + (pm25 - 60) * (100 / 30)
            elif pm25 <= 120:
                computed_aqi = 200 + (pm25 - 90) * (100 / 30)
            elif pm25 <= 250:
                computed_aqi = 300 + (pm25 - 120) * (100 / 130)
            else:
                computed_aqi = 400 + (pm25 - 250) * (100 / 130)
        else:
            computed_aqi = 100.0

        computed_aqi = max(0.0, round(computed_aqi, 1))
        category = get_aqi_category(computed_aqi)
        color = get_aqi_color(computed_aqi)
        health_message = get_health_message(computed_aqi)

        pollutants_dict = {
            "PM2.5": pm25,
            "PM10": pm10,
            "NO2": no2,
            "SO2": so2,
            "CO": co_mg,
            "O3": o3
        }

        dominant_info = identify_dominant_pollutant(pollutants_dict)
        measurement_time = current.get("time") or datetime.now().isoformat()

        return {
            "status": "success",
            "data_mode": "live",
            "location": resolved_name,
            "latitude": lat,
            "longitude": lon,
            "aqi": computed_aqi,
            "category": category,
            "color": color,
            "health_message": health_message,
            "dominant_pollutant": dominant_info["dominant"],
            "dominant_ratio": dominant_info["ratio_to_safe_limit"],
            "pollutants": {k: (round(v, 2) if v is not None else None) for k, v in pollutants_dict.items()},
            "measurement_time": measurement_time,
            "data_timestamp": measurement_time,
            "us_aqi": us_aqi,
            "european_aqi": european_aqi,
            "source": "Live Air Quality Data (Open-Meteo)"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Network or processing error fetching live air quality: {str(e)}",
            "location": resolved_name
        }
