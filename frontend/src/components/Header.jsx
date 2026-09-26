import { MapPin } from "lucide-react";
import { CITIES } from "../data/mockData";
import { CURRENT_LOCATION_VALUE } from "../services/locationService";

export function Header({
  activePage,
  selectedCity,
  locationMode = "city",
  resolvedLocationName = "",
  onLocationSelect,
}) {
  const titles = {
    dashboard: "Air Quality Dashboard",
    predict: "Predict AQI",
    analytics: "Air Quality Analytics",
    model: "Machine Learning Model",
    agent: "Autonomous AI Air Quality Advisor",
  };

  const subtitles = {
    dashboard: "Monitor, analyze and predict air quality using machine learning.",
    predict: "Enter pollutant levels to forecast AQI using our trained Random Forest pipeline.",
    analytics: "7-day trends, historical distributions and pollutant contribution breakdown.",
    model: "15-feature Random Forest Regressor architecture and evaluation benchmarks.",
    agent: "Ask natural-language questions to the multi-tool ReAct air quality intelligence agent.",
  };

  const selectValue =
    locationMode === "current" ? CURRENT_LOCATION_VALUE : selectedCity;

  return (
    <header className="header">
      <div>
        <p className="small-title">AIR QUALITY INTELLIGENCE</p>
        <h2>{titles[activePage] || "AirSense"}</h2>
        <p className="subtitle">{subtitles[activePage] || "Air Quality Monitoring & Prediction"}</p>
      </div>

      <div className="location">
        <span className="location-dot"></span>
        <MapPin size={15} style={{ opacity: 0.7, marginRight: 2 }} />
        <select
          value={selectValue}
          onChange={(e) => onLocationSelect(e.target.value)}
          aria-label="Select Monitoring City or Current Location"
          style={{
            border: "none",
            background: "transparent",
            font: "inherit",
            fontWeight: 600,
            color: "#385249",
            cursor: "pointer",
            outline: "none",
          }}
        >
          <option value={CURRENT_LOCATION_VALUE}>
            {locationMode === "current" && resolvedLocationName
              ? `Use my current location (${resolvedLocationName})`
              : "Use my current location"}
          </option>
          {CITIES.map((c) => (
            <option key={c.id} value={c.name}>
              {c.name}, India
            </option>
          ))}
        </select>
      </div>
    </header>
  );
}

export default Header;

