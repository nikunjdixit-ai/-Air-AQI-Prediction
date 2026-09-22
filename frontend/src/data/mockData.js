/**
 * Curated AirSense baseline mock data, city profiles, and CPCB standards.
 * Used for instant UI initialization and resilient offline fallback.
 */

export const CITIES = [
  { id: "kanpur", name: "Kanpur", state: "Uttar Pradesh", defaultAqi: 142 },
  { id: "delhi", name: "Delhi", state: "National Capital Territory", defaultAqi: 215 },
  { id: "mumbai", name: "Mumbai", state: "Maharashtra", defaultAqi: 98 },
  { id: "bengaluru", name: "Bengaluru", state: "Karnataka", defaultAqi: 68 },
  { id: "kolkata", name: "Kolkata", state: "West Bengal", defaultAqi: 135 },
  { id: "chennai", name: "Chennai", state: "Tamil Nadu", defaultAqi: 74 },
];

export const AQI_CATEGORIES = [
  { min: 0, max: 50, name: "Good", color: "#22c55e", bg: "#eefbf3", text: "#15803d", desc: "Air quality is considered satisfactory, and air pollution poses little or no risk." },
  { min: 51, max: 100, name: "Satisfactory", color: "#84cc16", bg: "#f7fee7", text: "#4d7c0f", desc: "Minor breathing discomfort to sensitive people." },
  { min: 101, max: 200, name: "Moderate", color: "#eab308", bg: "#fefce8", text: "#a16207", desc: "Breathing discomfort to people with lungs, asthma and heart diseases." },
  { min: 201, max: 300, name: "Poor", color: "#f97316", bg: "#fff7ed", text: "#c2410c", desc: "Breathing discomfort to most people on prolonged exposure." },
  { min: 301, max: 400, name: "Very Poor", color: "#ef4444", bg: "#fef2f2", text: "#b91c1c", desc: "Respiratory illness on prolonged exposure." },
  { min: 401, max: 500, name: "Severe", color: "#881337", bg: "#fff1f2", text: "#881337", desc: "Affects healthy people and seriously impacts those with existing diseases." },
];

export function getCategoryInfo(aqi) {
  const val = Number(aqi) || 0;
  if (val <= 50) return AQI_CATEGORIES[0];
  if (val <= 100) return AQI_CATEGORIES[1];
  if (val <= 200) return AQI_CATEGORIES[2];
  if (val <= 300) return AQI_CATEGORIES[3];
  if (val <= 400) return AQI_CATEGORIES[4];
  return AQI_CATEGORIES[5];
}

export const CITY_DEFAULTS = {
  Kanpur: {
    aqi: 142,
    category: "Moderate",
    description: "Air quality is acceptable; sensitive people may experience minor respiratory irritation.",
    weather: {
      temperature: "28°C",
      humidity: "64%",
      windSpeed: "8.4 km/h",
      trend: "+4.2% vs yesterday",
      dispersion: "Light breeze with normal dispersion",
    },
    pollutants: [
      { name: "PM2.5", value: 48.2, unit: "µg/m³", status: "Moderate" },
      { name: "PM10", value: 82.5, unit: "µg/m³", status: "Moderate" },
      { name: "NO₂", value: 31.4, unit: "µg/m³", status: "Good" },
      { name: "SO₂", value: 12.8, unit: "µg/m³", status: "Good" },
      { name: "CO", value: 0.8, unit: "mg/m³", status: "Good" },
      { name: "O₃", value: 42.1, unit: "µg/m³", status: "Good" },
    ],
    weeklyTrend: [
      { day: "Mon", aqi: 128 },
      { day: "Tue", aqi: 136 },
      { day: "Wed", aqi: 151 },
      { day: "Thu", aqi: 145 },
      { day: "Fri", aqi: 158 },
      { day: "Sat", aqi: 149 },
      { day: "Sun", aqi: 142 },
    ],
  },
  Delhi: {
    aqi: 215,
    category: "Poor",
    description: "Breathing discomfort likely for individuals with heart or respiratory ailments.",
    weather: {
      temperature: "31°C",
      humidity: "58%",
      windSpeed: "6.2 km/h",
      trend: "+7.8% vs yesterday",
      dispersion: "Stagnant boundary layer trapping particulates",
    },
    pollutants: [
      { name: "PM2.5", value: 92.4, unit: "µg/m³", status: "Poor" },
      { name: "PM10", value: 168.0, unit: "µg/m³", status: "Poor" },
      { name: "NO₂", value: 48.5, unit: "µg/m³", status: "Moderate" },
      { name: "SO₂", value: 18.2, unit: "µg/m³", status: "Good" },
      { name: "CO", value: 1.6, unit: "mg/m³", status: "Moderate" },
      { name: "O₃", value: 54.0, unit: "µg/m³", status: "Moderate" },
    ],
    weeklyTrend: [
      { day: "Mon", aqi: 188 },
      { day: "Tue", aqi: 195 },
      { day: "Wed", aqi: 210 },
      { day: "Thu", aqi: 228 },
      { day: "Fri", aqi: 240 },
      { day: "Sat", aqi: 225 },
      { day: "Sun", aqi: 215 },
    ],
  },
  Mumbai: {
    aqi: 98,
    category: "Satisfactory",
    description: "Air quality is satisfactory with coastal sea breeze keeping particulate dispersion healthy.",
    weather: {
      temperature: "30°C",
      humidity: "78%",
      windSpeed: "14.1 km/h",
      trend: "-3.1% vs yesterday",
      dispersion: "Strong sea-breeze ventilation",
    },
    pollutants: [
      { name: "PM2.5", value: 32.1, unit: "µg/m³", status: "Satisfactory" },
      { name: "PM10", value: 65.4, unit: "µg/m³", status: "Satisfactory" },
      { name: "NO₂", value: 24.0, unit: "µg/m³", status: "Good" },
      { name: "SO₂", value: 10.5, unit: "µg/m³", status: "Good" },
      { name: "CO", value: 0.6, unit: "mg/m³", status: "Good" },
      { name: "O₃", value: 28.5, unit: "µg/m³", status: "Good" },
    ],
    weeklyTrend: [
      { day: "Mon", aqi: 105 },
      { day: "Tue", aqi: 110 },
      { day: "Wed", aqi: 95 },
      { day: "Thu", aqi: 102 },
      { day: "Fri", aqi: 92 },
      { day: "Sat", aqi: 88 },
      { day: "Sun", aqi: 98 },
    ],
  },
  Bengaluru: {
    aqi: 68,
    category: "Satisfactory",
    description: "Air quality is good to satisfactory across most urban zones.",
    weather: {
      temperature: "24°C",
      humidity: "62%",
      windSpeed: "11.0 km/h",
      trend: "-1.5% vs yesterday",
      dispersion: "Mild plateau breeze with steady mixing",
    },
    pollutants: [
      { name: "PM2.5", value: 22.0, unit: "µg/m³", status: "Good" },
      { name: "PM10", value: 45.0, unit: "µg/m³", status: "Good" },
      { name: "NO₂", value: 18.2, unit: "µg/m³", status: "Good" },
      { name: "SO₂", value: 7.4, unit: "µg/m³", status: "Good" },
      { name: "CO", value: 0.5, unit: "mg/m³", status: "Good" },
      { name: "O₃", value: 22.1, unit: "µg/m³", status: "Good" },
    ],
    weeklyTrend: [
      { day: "Mon", aqi: 62 },
      { day: "Tue", aqi: 70 },
      { day: "Wed", aqi: 65 },
      { day: "Thu", aqi: 72 },
      { day: "Fri", aqi: 68 },
      { day: "Sat", aqi: 64 },
      { day: "Sun", aqi: 68 },
    ],
  },
};

export const MODEL_BENCHMARKS = [
  { model: "Linear Regression", mae: 31.68, mse: 3681.59, rmse: 60.68, r2: 0.7639, badge: "Baseline" },
  { model: "Decision Tree Regressor", mae: 27.96, mse: 3523.80, rmse: 59.36, r2: 0.7740, badge: "Nonlinear" },
  { model: "Random Forest Regressor", mae: 20.38, mse: 1829.06, rmse: 42.77, r2: 0.8827, badge: "Ensemble" },
  { model: "Tuned Random Forest", mae: 20.22, mse: 1751.51, rmse: 41.85, r2: 0.8877, badge: "Production Best", isBest: true },
];

export const MODEL_FEATURES = [
  { name: "PM2.5", role: "Primary input", description: "Fine inhalable particles (≤ 2.5 µm)", source: "Direct User Input" },
  { name: "PM10", role: "Primary input", description: "Coarse inhalable particles (≤ 10 µm)", source: "Direct User Input" },
  { name: "NO₂", role: "Primary input", description: "Nitrogen dioxide combustion emissions", source: "Direct User Input" },
  { name: "SO₂", role: "Primary input", description: "Sulfur dioxide industrial emissions", source: "Direct User Input" },
  { name: "CO", role: "Primary input", description: "Carbon monoxide vehicular exhaust", source: "Direct User Input" },
  { name: "O₃", role: "Primary input", description: "Ground-level photochemical ozone", source: "Direct User Input" },
  { name: "NO", role: "Secondary feature", description: "Nitric oxide precursor", source: "Auto-Imputed (Median: 15.0)" },
  { name: "NOx", role: "Secondary feature", description: "Total nitrogen oxides", source: "Auto-Imputed (Median: 30.0)" },
  { name: "NH3", role: "Secondary feature", description: "Ammonia agricultural/chemical emissions", source: "Auto-Imputed (Median: 20.0)" },
  { name: "Benzene", role: "Trace hydrocarbon", description: "Volatile organic compound (VOC)", source: "Auto-Imputed (Median: 2.5)" },
  { name: "Toluene", role: "Trace hydrocarbon", description: "Industrial solvent emission", source: "Auto-Imputed (Median: 6.0)" },
  { name: "Xylene", role: "Trace hydrocarbon", description: "Petrochemical solvent emission", source: "Auto-Imputed (Median: 2.0)" },
  { name: "Year", role: "Temporal feature", description: "Trend calendar year component", source: "System Calendar" },
  { name: "Month", role: "Temporal feature", description: "Seasonality month component (1-12)", source: "System Calendar" },
  { name: "Day", role: "Temporal feature", description: "Day of month component (1-31)", source: "System Calendar" },
];
