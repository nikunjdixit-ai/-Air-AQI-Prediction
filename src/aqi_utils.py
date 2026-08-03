def get_aqi_category(aqi):

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


def get_health_message(aqi):
    """Return a health recommendation based on AQI."""

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


def get_aqi_status(aqi):
    """Return category and health recommendation."""

    category = get_aqi_category(aqi)
    message = get_health_message(aqi)

    return {
        "aqi": round(aqi, 2),
        "category": category,
        "message": message
    }