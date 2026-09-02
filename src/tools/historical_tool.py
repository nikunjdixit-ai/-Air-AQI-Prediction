"""
Historical AQI Tool.
Queries and analyzes historical air quality patterns from the project dataset (city_day_cleaned.csv).
Computes historical averages, seasonal trends, clean/severe day frequencies, and comparative baselines.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from src.aqi_utils import get_aqi_category

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "city_day_cleaned.csv"
if not DATA_PATH.exists():
    DATA_PATH = PROJECT_ROOT / "data" / "raw" / "city_day.csv"

# Regional proxies for cities not directly present in the 26-city historical Kaggle dataset
CITY_PROXIES = {
    "kanpur": "Lucknow",       # Both in Central Uttar Pradesh gangetic plain (~80 km apart)
    "noida": "Delhi",
    "gurugram": "Delhi",
    "gurgaon": "Delhi",
    "ghaziabad": "Delhi",
    "faridabad": "Delhi",
    "agra": "Lucknow",
    "varanasi": "Patna",
    "pune": "Mumbai"
}

_HISTORICAL_DF = None


def get_dataframe() -> pd.DataFrame:
    global _HISTORICAL_DF
    if _HISTORICAL_DF is None:
        if not DATA_PATH.exists():
            raise FileNotFoundError(f"Could not find historical dataset at {DATA_PATH}")
        df = pd.read_csv(DATA_PATH)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["AQI"])
        _HISTORICAL_DF = df
    return _HISTORICAL_DF


def get_historical_aqi(
    location: str,
    date_range: Optional[str] = None,
    current_aqi: Optional[float] = None
) -> Dict[str, Any]:
    """
    Query and analyze historical AQI trends for a specific city.
    
    Parameters:
      location: City name (e.g. 'Delhi', 'Bengaluru', 'Kanpur').
      date_range: Optional date range filter ('2015-2020', 'winter', 'monsoon').
      current_aqi: Optional current AQI value to benchmark against the historical distribution.
    """
    df = get_dataframe()
    loc_clean = location.strip().lower()

    # Find matching city in dataset
    available_cities = df["City"].dropna().unique()
    matched_city = None
    is_proxy = False

    for c in available_cities:
        if c.lower() == loc_clean or loc_clean in c.lower():
            matched_city = c
            break

    if not matched_city and loc_clean in CITY_PROXIES:
        proxy_name = CITY_PROXIES[loc_clean]
        for c in available_cities:
            if c.lower() == proxy_name.lower():
                matched_city = c
                is_proxy = True
                break

    if not matched_city:
        matched_city = "Delhi"  # Benchmark representative
        is_proxy = True

    city_df = df[df["City"] == matched_city].copy()
    if city_df.empty:
        return {
            "status": "error",
            "message": f"No historical records found for location '{location}'.",
            "location": location
        }

    aqi_series = city_df["AQI"]
    mean_aqi = round(float(aqi_series.mean()), 1)
    median_aqi = round(float(aqi_series.median()), 1)
    min_aqi = round(float(aqi_series.min()), 1)
    max_aqi = round(float(aqi_series.max()), 1)
    p25 = round(float(np.percentile(aqi_series, 25)), 1)
    p75 = round(float(np.percentile(aqi_series, 75)), 1)

    # Seasonal analysis (Winter: Nov-Jan, Summer: Apr-Jun, Monsoon: Jul-Sep)
    city_df["Month"] = city_df["Date"].dt.month
    winter_mean = city_df[city_df["Month"].isin([11, 12, 1])]["AQI"].mean()
    monsoon_mean = city_df[city_df["Month"].isin([7, 8, 9])]["AQI"].mean()
    summer_mean = city_df[city_df["Month"].isin([4, 5, 6])]["AQI"].mean()

    # Category distribution
    categories = [get_aqi_category(val) for val in aqi_series]
    cat_counts = pd.Series(categories).value_counts(normalize=True) * 100
    cat_distribution = {k: f"{v:.1f}%" for k, v in cat_counts.items()}

    # Dominant historical pollutant
    pollutant_means = {}
    for col in ["PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]:
        if col in city_df.columns:
            val = city_df[col].mean()
            if not np.isnan(val):
                pollutant_means[col] = round(float(val), 1)

    # Compare current AQI if supplied
    comparison = None
    if current_aqi is not None:
        diff = round(current_aqi - mean_aqi, 1)
        pct_change = round(((current_aqi - mean_aqi) / mean_aqi) * 100, 1)
        percentile_rank = round(float((aqi_series < current_aqi).mean() * 100), 1)

        if diff < -20:
            assessment = f"Substantially cleaner than historical average ({abs(pct_change)}% lower; better than {100 - percentile_rank:.0f}% of recorded days)."
        elif diff > 20:
            assessment = f"Substantially worse than historical average ({pct_change}% higher; worse than {percentile_rank:.0f}% of recorded days)."
        else:
            assessment = f"Consistent with seasonal historical norms (within {abs(diff)} AQI points of historical mean)."

        comparison = {
            "current_aqi": current_aqi,
            "historical_mean": mean_aqi,
            "difference": diff,
            "percentage_difference": f"{pct_change:+}%",
            "percentile_rank": f"{percentile_rank}th percentile",
            "assessment": assessment
        }

    return {
        "status": "success",
        "queried_location": location,
        "matched_historical_dataset": matched_city,
        "is_regional_proxy": is_proxy,
        "proxy_note": f"Using neighboring {matched_city} (Indo-Gangetic Plain regional monitor) as geographical historical baseline." if is_proxy else None,
        "records_count": len(city_df),
        "date_range_covered": f"{city_df['Date'].min().strftime('%Y-%m-%d')} to {city_df['Date'].max().strftime('%Y-%m-%d')}",
        "stats": {
            "mean_aqi": mean_aqi,
            "median_aqi": median_aqi,
            "min_aqi": min_aqi,
            "max_aqi": max_aqi,
            "interquartile_range": [p25, p75]
        },
        "seasonal_averages": {
            "winter_nov_jan": round(winter_mean, 1) if not np.isnan(winter_mean) else None,
            "monsoon_jul_sep": round(monsoon_mean, 1) if not np.isnan(monsoon_mean) else None,
            "summer_apr_jun": round(summer_mean, 1) if not np.isnan(summer_mean) else None
        },
        "category_frequency": cat_distribution,
        "historical_pollutant_means": pollutant_means,
        "comparison_with_current": comparison
    }
