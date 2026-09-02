"""
Agent Tools Registry.
Defines OpenAI-compatible tool specifications for LLM function calling
and provides a unified execution dispatcher for all 5 intelligence tools.
"""

from typing import Any, Callable, Dict, List
from src.tools.health_knowledge_tool import get_aqi_health_guidance
from src.tools.historical_tool import get_historical_aqi
from src.tools.live_aqi_tool import fetch_live_air_quality
from src.tools.prediction_tool import predict_aqi_tool
from src.tools.weather_tool import fetch_weather_forecast

# Standard OpenAI-format tool schemas
AGENT_TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "fetch_live_air_quality",
            "description": "Fetch real-time air quality metrics, AQI, and pollutant concentrations (PM2.5, PM10, NO2, SO2, CO, O3) for a city from live monitoring APIs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City or place name, e.g., 'Kanpur', 'Delhi', 'Bengaluru'."
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_weather_forecast",
            "description": "Retrieve current weather and 3-day forecast (temperature, humidity, wind speed, precipitation, and atmospheric dispersion index) for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City or place name, e.g., 'Delhi', 'Kanpur'."
                    },
                    "date_or_time": {
                        "type": "string",
                        "description": "Optional date or timeframe indicator, e.g. 'today', 'tomorrow', or 'YYYY-MM-DD'."
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "predict_aqi_tool",
            "description": "Use the project's trained Machine Learning Random Forest pipeline to forecast AQI using pollutant levels or automatic city baselines.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City to predict AQI for using current sensor baselines."
                    },
                    "target_date": {
                        "type": "string",
                        "description": "Target date for prediction, e.g., 'today', 'tomorrow', or 'YYYY-MM-DD'."
                    },
                    "input_data": {
                        "type": "object",
                        "description": "Optional dictionary of custom pollutant readings (PM2.5, PM10, etc.) if explicitly specified by user."
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_historical_aqi",
            "description": "Query multi-year historical AQI data, seasonal patterns (winter vs monsoon), cleanest/worst records, and benchmark current readings against historical distributions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name to inspect historical records for."
                    },
                    "date_range": {
                        "type": "string",
                        "description": "Optional filter like 'winter', 'monsoon', 'seasonal'."
                    },
                    "current_aqi": {
                        "type": "number",
                        "description": "Optional current AQI to compare against the historical percentile distribution."
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_aqi_health_guidance",
            "description": "Retrieve authoritative health recommendations, medical risk advisories (asthma, COPD, cardiovascular), exercise advice (running, cycling), and mask recommendations based on CPCB and WHO standards.",
            "parameters": {
                "type": "object",
                "properties": {
                    "aqi": {
                        "type": "number",
                        "description": "Numeric AQI to evaluate."
                    },
                    "category": {
                        "type": "string",
                        "description": "AQI category name (e.g., 'Moderate', 'Poor', 'Severe')."
                    },
                    "condition": {
                        "type": "string",
                        "description": "Specific health vulnerability (e.g. 'asthma', 'heart disease', 'pregnancy', 'elderly')."
                    },
                    "activity": {
                        "type": "string",
                        "description": "Specific outdoor activity (e.g. 'running', 'cycling', 'morning walk')."
                    },
                    "target_pollutant": {
                        "type": "string",
                        "description": "Optional specific pollutant to explain (e.g., 'PM2.5', 'O3', 'NO2')."
                    }
                }
            }
        }
    }
]

TOOL_MAPPING: Dict[str, Callable] = {
    "fetch_live_air_quality": fetch_live_air_quality,
    "fetch_weather_forecast": fetch_weather_forecast,
    "predict_aqi_tool": predict_aqi_tool,
    "get_historical_aqi": get_historical_aqi,
    "get_aqi_health_guidance": get_aqi_health_guidance
}


def dispatch_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a registered tool with provided arguments safely."""
    func = TOOL_MAPPING.get(tool_name)
    if not func:
        return {
            "status": "error",
            "message": f"Tool '{tool_name}' is not recognized by the agent registry."
        }
    try:
        return func(**arguments)
    except Exception as e:
        return {
            "status": "error",
            "message": f"Execution error in tool '{tool_name}': {str(e)}"
        }
