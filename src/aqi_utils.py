"""
AQI Utilities and Standards Module.
Adheres to Central Pollution Control Board (CPCB) India and WHO Air Quality standards.
"""

from typing import Any, Dict, Optional

AQI_BREAKPOINTS = [
    (0, 50, "Good", "#00E400", "Air quality is good. Enjoy normal outdoor activities."),
    (51, 100, "Satisfactory", "#92D050", "Air quality is satisfactory. Sensitive individuals should be cautious."),
    (101, 200, "Moderate", "#FFCC00", "Acceptable air quality; however, sensitive individuals may experience minor breathing discomfort."),
    (201, 300, "Poor", "#FF7E00", "Avoid prolonged outdoor exertion. People with heart/lung disease are at greater risk."),
    (301, 400, "Very Poor", "#FF0000", "Significant respiratory illness risk. Avoid all strenuous outdoor activities."),
    (401, 9999, "Severe", "#7E0023", "Emergency health warning. Air quality is hazardous. Remain strictly indoors.")
]

# Standard 24-hour CPCB threshold standards in ug/m3
STANDARD_THRESHOLDS = {
    "PM2.5": 60.0,
    "PM10": 100.0,
    "NO2": 80.0,
    "SO2": 80.0,
    "CO": 2.0,       # mg/m3
    "O3": 100.0,
    "NH3": 400.0
}


def get_aqi_category(aqi: float) -> str:
    """Return standard CPCB AQI category."""
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Satisfactory"
    elif aqi <= 200:
        return "Moderate"
    elif aqi <= 300:
        return "Poor"
    elif aqi <= 400:
        return "Very Poor"
    else:
        return "Severe"


def get_aqi_color(aqi: float) -> str:
    """Return hex color code associated with AQI level."""
    for low, high, _, color, _ in AQI_BREAKPOINTS:
        if low <= aqi <= high:
            return color
    return "#7E0023"


def get_health_message(aqi: float) -> str:
    """Return general health recommendation based on AQI."""
    if aqi <= 50:
        return "Air quality is good. Enjoy normal outdoor activities."
    elif aqi <= 100:
        return "Air quality is satisfactory. Sensitive individuals should be cautious."
    elif aqi <= 200:
        return "Sensitive individuals should reduce prolonged outdoor activity."
    elif aqi <= 300:
        return "Avoid prolonged outdoor activity, especially if you are sensitive to air pollution."
    elif aqi <= 400:
        return "Avoid outdoor activities when possible. Health effects may occur for everyone."
    else:
        return "Avoid outdoor exposure. The air quality is hazardous."


def get_detailed_health_advisory(
    aqi: float,
    condition: Optional[str] = None,
    activity: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate tailored medical and activity advisories based on AQI, health profile, and planned activities.
    """
    category = get_aqi_category(aqi)
    color = get_aqi_color(aqi)
    
    # Base recommendation
    is_safe_for_exercise = aqi <= 150
    mask_recommended = aqi > 150
    air_purifier_recommended = aqi > 200
    
    # Specific activities
    activity_advice = "Normal outdoor routines are safe."
    if activity and ("run" in activity.lower() or "jog" in activity.lower() or "exercis" in activity.lower() or "cycl" in activity.lower()):
        if aqi <= 100:
            activity_advice = "Great conditions for outdoor running and exercise."
        elif aqi <= 150:
            activity_advice = "Outdoor exercise is acceptable, but consider reducing intensity or duration if you feel fatigue."
        elif aqi <= 200:
            activity_advice = "Move high-intensity cardiovascular workouts indoors or exercise early before photochemical smog builds up."
        else:
            activity_advice = "Outdoor running/exercise is NOT recommended today. Heavy breathing will deposit toxic particulates deep in lungs. Exercise indoors."
            is_safe_for_exercise = False

    # Specific health conditions
    condition_advice = "No elevated vulnerability identified."
    if condition:
        cond_lower = condition.lower()
        if any(w in cond_lower for w in ["asthma", "copd", "respiratory", "bronchitis"]):
            if aqi > 100:
                condition_advice = "High risk for asthma/respiratory flare-ups: keep rescue inhalers nearby and minimize outdoor exposure."
            else:
                condition_advice = "Respiratory conditions: clean air, but monitor symptom onset."
        elif any(w in cond_lower for w in ["heart", "cardio", "blood pressure"]):
            if aqi > 150:
                condition_advice = "Cardiovascular alert: elevated particulate matter increases blood pressure and cardiac strain. Stay in filtered air."
        elif any(w in cond_lower for w in ["child", "kid", "baby", "elder", "senior", "pregnant"]):
            if aqi > 100:
                condition_advice = "Vulnerable demographics (children/elderly/expecting mothers) should limit outdoor playtime and walking."

    return {
        "aqi": round(aqi, 1),
        "category": category,
        "color": color,
        "general_message": get_health_message(aqi),
        "is_safe_for_exercise": is_safe_for_exercise,
        "mask_recommended": mask_recommended,
        "recommended_mask": "N95 / FFP2" if mask_recommended else "None required",
        "air_purifier_recommended": air_purifier_recommended,
        "activity_advice": activity_advice,
        "condition_advice": condition_advice
    }


def identify_dominant_pollutant(pollutants: Dict[str, float]) -> Dict[str, Any]:
    """
    Identify the pollutant that poses the greatest risk relative to national air quality benchmarks.
    """
    if not pollutants:
        return {"dominant": "Unknown", "ratio": 1.0, "details": {}}
    
    ratios = {}
    for pol, val in pollutants.items():
        if val is None:
            continue
        std_key = pol.replace(".", "").upper()
        # Look up standard threshold
        threshold = None
        for k, v in STANDARD_THRESHOLDS.items():
            if k.replace(".", "").upper() == std_key:
                threshold = v
                break
        if threshold and threshold > 0:
            ratios[pol] = round(val / threshold, 2)
        else:
            ratios[pol] = round(val / 100.0, 2)
            
    if not ratios:
        return {"dominant": "PM2.5", "ratio": 1.0, "ratios": {}}
        
    dominant = max(ratios, key=ratios.get)
    return {
        "dominant": dominant,
        "ratio_to_safe_limit": ratios[dominant],
        "all_ratios": ratios
    }


def get_aqi_status(aqi: float) -> Dict[str, Any]:
    """Return category, color, and health recommendation (Backwards-compatible)."""
    category = get_aqi_category(aqi)
    message = get_health_message(aqi)

    return {
        "aqi": round(aqi, 2),
        "category": category,
        "message": message,
        "color": get_aqi_color(aqi)
    }
