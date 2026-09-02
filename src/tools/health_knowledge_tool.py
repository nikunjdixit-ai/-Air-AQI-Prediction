"""
AQI & Health Knowledge Tool.
Provides authoritative health advisories, medical risk profiles, and activity guidance
grounded in CPCB (India) and WHO (2021) Air Quality Guidelines.
"""

from typing import Any, Dict, List, Optional
from src.aqi_utils import get_aqi_category, get_detailed_health_advisory

# Comprehensive descriptions and health impacts of major pollutants
POLLUTANT_KNOWLEDGE_BASE = {
    "PM2.5": {
        "full_name": "Fine Particulate Matter (< 2.5 micrometers)",
        "sources": "Vehicle exhaust, biomass burning, coal-fired power plants, construction dust.",
        "health_impact": "Deep alveolar penetration into lung capillaries and bloodstream. Increases systemic inflammation, myocardial infarction risk, stroke, and exacerbates asthma.",
        "who_guideline_24h": "15 ug/m3",
        "cpcb_standard_24h": "60 ug/m3"
    },
    "PM10": {
        "full_name": "Coarse Particulate Matter (< 10 micrometers)",
        "sources": "Road dust, construction, agricultural burning, windblown dust.",
        "health_impact": "Deposits in upper respiratory tract, bronchi, and trachea, causing coughing, wheezing, and bronchitis.",
        "who_guideline_24h": "45 ug/m3",
        "cpcb_standard_24h": "100 ug/m3"
    },
    "NO2": {
        "full_name": "Nitrogen Dioxide",
        "sources": "High-temperature internal combustion engines, vehicular traffic.",
        "health_impact": "Potent airway irritant. Induces bronchospasm in asthmatics, decreases lung function, and acts as an ozone precursor.",
        "who_guideline_24h": "25 ug/m3",
        "cpcb_standard_24h": "80 ug/m3"
    },
    "SO2": {
        "full_name": "Sulphur Dioxide",
        "sources": "Combustion of sulphur-containing fossil fuels (coal, diesel, refineries).",
        "health_impact": "Causes severe bronchoconstriction within minutes of inhalation, eye irritation, and acid rain formation.",
        "who_guideline_24h": "40 ug/m3",
        "cpcb_standard_24h": "80 ug/m3"
    },
    "CO": {
        "full_name": "Carbon Monoxide",
        "sources": "Incomplete combustion in motor vehicles, faulty heating systems.",
        "health_impact": "Binds with hemoglobin to form carboxyhemoglobin, impairing oxygen delivery to brain and heart tissue.",
        "who_guideline_24h": "4 mg/m3",
        "cpcb_standard_24h": "2 mg/m3"
    },
    "O3": {
        "full_name": "Ground-Level Tropospheric Ozone",
        "sources": "Secondary photochemical pollutant formed by sunlight reacting with NOx and VOCs.",
        "health_impact": "Strong oxidant that damages lung tissues, reduces vital capacity, and triggers chest pain during deep inhalation.",
        "who_guideline_8h": "100 ug/m3",
        "cpcb_standard_8h": "100 ug/m3"
    }
}


def get_aqi_health_guidance(
    aqi: Optional[float] = None,
    category: Optional[str] = None,
    condition: Optional[str] = None,
    activity: Optional[str] = None,
    target_pollutant: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieve authoritative health recommendations, medical precautions, and pollutant mechanisms.
    
    Parameters:
      aqi: Numeric AQI value.
      category: AQI category string if aqi is not directly available.
      condition: Specific health vulnerability (e.g. 'asthma', 'copd', 'heart disease', 'pregnancy', 'child').
      activity: Planned activity (e.g. 'running', 'morning walk', 'cycling', 'outdoor school event').
      target_pollutant: Specific pollutant to explain (e.g. 'PM2.5', 'O3', 'NO2').
    """
    if aqi is None:
        category_map = {
            "good": 35.0,
            "satisfactory": 75.0,
            "moderate": 150.0,
            "poor": 250.0,
            "very poor": 350.0,
            "severe": 450.0
        }
        aqi = category_map.get((category or "moderate").lower().strip(), 120.0)

    advisory = get_detailed_health_advisory(aqi, condition=condition, activity=activity)

    # Attach pollutant knowledge if requested
    pollutant_detail = None
    if target_pollutant:
        clean_pol = target_pollutant.replace(".", "").upper()
        for k, v in POLLUTANT_KNOWLEDGE_BASE.items():
            if k.replace(".", "").upper() == clean_pol:
                pollutant_detail = v
                pollutant_detail["pollutant_code"] = k
                break

    return {
        "status": "success",
        "aqi_evaluated": aqi,
        "category": advisory["category"],
        "advisory": advisory,
        "pollutant_details": pollutant_detail,
        "regulatory_standards": "Central Pollution Control Board (CPCB) India / World Health Organization (WHO 2021)"
    }
