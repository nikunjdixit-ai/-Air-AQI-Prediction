/**
 * AirSense AQI Service
 * High-level service layer connecting React components to Flask REST APIs.
 */

import { apiRequest } from "../api/client";
import { CITY_DEFAULTS, getCategoryInfo } from "../data/mockData";

/**
 * Check backend and ML model availability.
 */
export async function checkHealth() {
  const res = await apiRequest("/health", { method: "GET" }, 6000);
  if (res.success && res.data) {
    return {
      online: res.data.status === "healthy",
      version: res.data.version || "1.1.0",
      modelLoaded: Boolean(res.data.model_loaded),
      service: res.data.service,
    };
  }
  return {
    online: false,
    version: null,
    modelLoaded: false,
    error: res.error,
  };
}

function formatLiveTimestamp(isoOrTimeStr) {
  if (!isoOrTimeStr) return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  try {
    const dt = new Date(isoOrTimeStr);
    if (!Number.isNaN(dt.getTime())) {
      return dt.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    }
  } catch {
    // ignore parse failure
  }
  return String(isoOrTimeStr);
}

/**
 * Fetch live sensor telemetry & atmospheric conditions for a given city or geographic coordinates.
 * Gracefully falls back to curated city baseline if backend/API is temporarily unreachable,
 * explicitly tagging the response with `dataMode: "live"` or `dataMode: "offline_baseline"`.
 *
 * @param {string | { lat: number, lon: number, city?: string }} queryOrCity
 */
export async function getLiveAQI(queryOrCity = "Kanpur") {
  let endpoint = "/live?city=Kanpur";
  let fallbackCityName = "Kanpur";

  if (
    queryOrCity &&
    typeof queryOrCity === "object" &&
    queryOrCity.lat != null &&
    queryOrCity.lon != null
  ) {
    const lat = Number(queryOrCity.lat);
    const lon = Number(queryOrCity.lon);
    fallbackCityName = queryOrCity.city || "Kanpur";
    endpoint = `/live?lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}`;
  } else if (typeof queryOrCity === "string" && queryOrCity.trim() !== "") {
    fallbackCityName = queryOrCity.trim().replace(/,\s*India$/i, "");
    endpoint = `/live?city=${encodeURIComponent(fallbackCityName)}`;
  }

  const res = await apiRequest(endpoint, { method: "GET" }, 25000);

  if (res.success && res.data && res.data.status === "success") {
    const raw = res.data;
    const pols = raw.pollutants || {};
    const weather = raw.weather || {};

    // Standardize pollutants array
    const pollutantList = [
      {
        name: "PM2.5",
        value: pols["PM2.5"] != null ? Number(Number(pols["PM2.5"]).toFixed(1)) : "—",
        unit: "µg/m³",
        status: pols["PM2.5"] > 60 ? (pols["PM2.5"] > 120 ? "Poor" : "Moderate") : "Good",
      },
      {
        name: "PM10",
        value: pols["PM10"] != null ? Number(Number(pols["PM10"]).toFixed(1)) : "—",
        unit: "µg/m³",
        status: pols["PM10"] > 100 ? (pols["PM10"] > 250 ? "Poor" : "Moderate") : "Good",
      },
      {
        name: "NO₂",
        value: pols["NO2"] != null ? Number(Number(pols["NO2"]).toFixed(1)) : "—",
        unit: "µg/m³",
        status: pols["NO2"] > 80 ? "Moderate" : "Good",
      },
      {
        name: "SO₂",
        value: pols["SO2"] != null ? Number(Number(pols["SO2"]).toFixed(1)) : "—",
        unit: "µg/m³",
        status: pols["SO2"] > 80 ? "Moderate" : "Good",
      },
      {
        name: "CO",
        value: pols["CO"] != null ? Number(Number(pols["CO"]).toFixed(2)) : "—",
        unit: "mg/m³",
        status: pols["CO"] > 2.0 ? "Moderate" : "Good",
      },
      {
        name: "O₃",
        value: pols["O3"] != null ? Number(Number(pols["O3"]).toFixed(1)) : "—",
        unit: "µg/m³",
        status: pols["O3"] > 100 ? "Moderate" : "Good",
      },
    ];

    const rawAqi = raw.aqi ?? raw.us_aqi ?? raw.european_aqi ?? 100;
    const cat = getCategoryInfo(rawAqi);
    const resolvedLocation = raw.location || `${fallbackCityName}, India`;

    return {
      success: true,
      dataMode: "live",
      isFallback: false,
      city: resolvedLocation,
      latitude: raw.latitude,
      longitude: raw.longitude,
      aqi: Math.round(Number(rawAqi)),
      category: cat.name,
      categoryColor: cat.color,
      categoryBg: cat.bg,
      description: raw.health_message || cat.desc,
      dominantPollutant: raw.dominant_pollutant || "PM2.5",
      weather: {
        temperature:
          weather.temperature != null ? `${Math.round(Number(weather.temperature))}°C` : "—",
        humidity:
          weather.relative_humidity != null ? `${Math.round(Number(weather.relative_humidity))}%` : "—",
        windSpeed:
          weather.wind_speed != null ? `${Number(weather.wind_speed).toFixed(1)} km/h` : "—",
        trend: raw.dispersion_index || weather.condition || "Live sensor reading",
        dispersion: raw.dispersion_index || weather.dispersion || "Unavailable",
      },
      pollutants: pollutantList,
      source: "Live Air Quality Data",
      timestamp: formatLiveTimestamp(raw.data_timestamp || raw.measurement_time),
      rawTimestamp: raw.data_timestamp || raw.measurement_time || null,
    };
  }

  // Graceful fallback to calibrated offline city baseline profile
  const cleanKey = Object.keys(CITY_DEFAULTS).find(
    (k) => k.toLowerCase() === fallbackCityName.toLowerCase()
  );
  const fallback = (cleanKey && CITY_DEFAULTS[cleanKey]) || CITY_DEFAULTS["Kanpur"];
  const cat = getCategoryInfo(fallback.aqi);

  return {
    success: false,
    dataMode: "offline_baseline",
    isFallback: true,
    fallbackReason:
      res.error ||
      "Live air-quality data is currently unavailable. Showing a calibrated baseline profile.",
    city: cleanKey || fallbackCityName,
    aqi: fallback.aqi,
    category: fallback.category,
    categoryColor: cat.color,
    categoryBg: cat.bg,
    description: fallback.description,
    dominantPollutant: "PM2.5",
    weather: fallback.weather,
    pollutants: fallback.pollutants,
    source: "Offline City Baseline",
    timestamp: "—",
  };
}

/**
 * Submit pollutant values to Flask ML inference endpoint (/predict).
 */
export async function predictAQI(formData, cityName = "Delhi", targetDate = "today") {
  // Normalize frontend keys to canonical model names
  const payload = {
    location: cityName,
    target_date: targetDate,
    "PM2.5": formData.pm25 !== "" && formData.pm25 != null ? Number(formData.pm25) : undefined,
    "PM10": formData.pm10 !== "" && formData.pm10 != null ? Number(formData.pm10) : undefined,
    "NO2": formData.no2 !== "" && formData.no2 != null ? Number(formData.no2) : undefined,
    "SO2": formData.so2 !== "" && formData.so2 != null ? Number(formData.so2) : undefined,
    "CO": formData.co !== "" && formData.co != null ? Number(formData.co) : undefined,
    "O3": formData.o3 !== "" && formData.o3 != null ? Number(formData.o3) : undefined,
  };

  const res = await apiRequest("/predict", {
    method: "POST",
    body: JSON.stringify(payload),
  }, 15000);

  if (!res.success) {
    throw new Error(res.error || "Prediction request failed.");
  }

  const data = res.data;
  const cat = getCategoryInfo(data.aqi);

  const rawFactors = data.factor_contributions || data.major_factors || [];
  const normalizedFactors = rawFactors.map((f) => ({
    pollutant: f.pollutant,
    percentage: f.percentage != null ? f.percentage : Math.round(Math.min(100, (f.ratio_to_safe_limit || 0.5) * 60)),
    is_dominant: f.is_dominant ?? (f.pollutant === data.dominant_pollutant),
    impact: f.impact_level || "Moderate",
  }));

  return {
    aqi: Math.round(data.aqi * 10) / 10,
    roundedAqi: Math.round(data.aqi),
    category: data.category || cat.name,
    categoryColor: data.category_color || cat.color,
    categoryBg: cat.bg,
    healthMessage: data.health_message || cat.desc,
    dominantPollutant: data.dominant_pollutant || "PM2.5",
    locationContext: data.location_context || cityName,
    targetDate: data.target_date || targetDate,
    factorContributions: normalizedFactors,
    modelMeta: {
      algorithm: "Random Forest Regressor (Tuned)",
      featuresUsed: 15,
      imputedNotice: "6 secondary pollutants & calendar features auto-imputed from national baselines",
    },
  };
}

/**
 * Fetch historical AQI trends & seasonal distributions (/historical).
 */
export async function getHistoricalAQI(cityName = "Delhi") {
  const res = await apiRequest(`/historical?city=${encodeURIComponent(cityName)}`, { method: "GET" }, 8000);
  if (res.success && res.data && res.data.status === "success") {
    return res.data;
  }
  return null;
}

/**
 * Consult the autonomous Air Quality Intelligence ReAct agent (/agent).
 */
export async function askAgent(query) {
  if (!query || !query.trim()) {
    throw new Error("Query cannot be empty.");
  }

  const res = await apiRequest("/agent", {
    method: "POST",
    body: JSON.stringify({ query: query.trim() }),
  }, 25000);

  if (!res.success) {
    throw new Error(res.error || "Agent failed to respond.");
  }

  return {
    response: res.data.response,
    activity: res.data.activity || [],
    toolOutputs: res.data.tool_outputs || {},
    location: res.data.location,
  };
}
