import { useEffect, useState } from "react";
import {
  Activity,
  ArrowRight,
  Cloud,
  Droplets,
  RefreshCw,
  Wind,
} from "lucide-react";
import { getLiveAQI } from "../services/aqiService";

export function Dashboard({ navigateTo, selectedCity }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isCancelled = false;
    getLiveAQI(selectedCity)
      .then((result) => {
        if (!isCancelled) {
          setData(result);
          setLoading(false);
        }
      })
      .catch(() => {
        if (!isCancelled) {
          setLoading(false);
        }
      });

    return () => {
      isCancelled = true;
    };
  }, [selectedCity]);

  const handleRefresh = async () => {
    setLoading(true);
    try {
      const result = await getLiveAQI(selectedCity);
      setData(result);
    } finally {
      setLoading(false);
    }
  };

  // Compute progress bar width (max 400 scale)
  const aqiVal = data?.aqi || 142;
  const progressPercent = Math.min(100, Math.max(8, (aqiVal / 400) * 100));

  return (
    <>
      {data?.isFallback && (
        <div
          style={{
            background: "#fffbeb",
            border: "1px solid #fde68a",
            color: "#92400e",
            borderRadius: 12,
            padding: "10px 16px",
            marginBottom: 20,
            fontSize: 12,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <span>
            ⚠️ <strong>Offline Baseline Mode:</strong> Live station currently unreachable. Showing calibrated baseline profile for {selectedCity}.
          </span>
          <button
            onClick={handleRefresh}
            style={{
              background: "transparent",
              border: "none",
              color: "#92400e",
              fontWeight: 700,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: 4,
            }}
          >
            <RefreshCw size={12} /> Retry
          </button>
        </div>
      )}

      <section className="top-grid">
        <div className="aqi-card">
          <div className="card-heading">
            <div>
              <p className="label">CURRENT AIR QUALITY</p>
              <h3>Air Quality Index</h3>
            </div>

            <div className="aqi-icon">
              <Wind size={24} />
            </div>
          </div>

          <div className="aqi-value">
            {loading ? <span style={{ opacity: 0.5 }}>...</span> : aqiVal}
          </div>

          <div className="aqi-status">
            <span
              style={{
                backgroundColor: data?.categoryColor || "#84cc16",
              }}
            ></span>
            {data?.category || "Moderate"}
          </div>

          <p className="aqi-description">
            {data?.description ||
              "Air quality is acceptable; sensitive individuals may experience minor respiratory irritation."}
          </p>

          <div className="aqi-bar">
            <div className="bar-background">
              <div
                className="bar-progress"
                style={{
                  width: `${progressPercent}%`,
                  backgroundColor: data?.categoryColor || "#1f8f63",
                  transition: "width 0.4s ease",
                }}
              ></div>
            </div>

            <div className="bar-labels">
              <span>Good</span>
              <span>Moderate</span>
              <span>Poor</span>
              <span>Very Poor</span>
            </div>
          </div>
        </div>

        <div className="weather-grid">
          <InfoCard
            icon={<Cloud size={20} />}
            title="Temperature"
            value={data?.weather?.temperature || "28°C"}
            description={loading ? "Refreshing..." : "Atmospheric condition"}
          />

          <InfoCard
            icon={<Droplets size={20} />}
            title="Humidity"
            value={data?.weather?.humidity || "64%"}
            description="Relative humidity"
          />

          <InfoCard
            icon={<Wind size={20} />}
            title="Wind Speed"
            value={data?.weather?.windSpeed || "8.4 km/h"}
            description="Ventilation velocity"
          />

          <InfoCard
            icon={<Activity size={20} />}
            title="AQI Trend / Mixing"
            value={data?.weather?.trend || "+4.2%"}
            description="Atmospheric dispersion index"
          />
        </div>
      </section>

      <section className="section">
        <div className="section-heading">
          <div>
            <p className="label">CURRENT READINGS</p>
            <h3>Pollutant Levels ({selectedCity})</h3>
          </div>

          <button
            className="view-button"
            onClick={() => navigateTo("analytics")}
          >
            View analytics →
          </button>
        </div>

        <div className="pollutant-grid">
          {(data?.pollutants || []).map((p) => (
            <Pollutant
              key={p.name}
              name={p.name}
              value={p.value}
              unit={p.unit}
              status={p.status}
            />
          ))}
        </div>
      </section>

      <section className="prediction-banner">
        <div>
          <p className="label">MACHINE LEARNING</p>
          <h3>Predict the next AQI value</h3>
          <p>
            Use pollutant and environmental readings to generate an AQI prediction
            with our trained Random Forest pipeline ($R^2 = 0.8877$).
          </p>
        </div>

        <button
          className="primary-button"
          onClick={() => navigateTo("predict")}
        >
          Predict AQI
          <ArrowRight size={17} />
        </button>
      </section>
    </>
  );
}

function InfoCard({ icon, title, value, description }) {
  return (
    <div className="info-card">
      <div className="info-icon">{icon}</div>
      <p>{title}</p>
      <h4>{value}</h4>
      <span>{description}</span>
    </div>
  );
}

function Pollutant({ name, value, unit, status }) {
  return (
    <div className="pollutant-card">
      <div className="pollutant-top">
        <div className="pollutant-icon">
          <Activity size={17} />
        </div>

        <span className={`status ${(status || "good").toLowerCase().replace(" ", "-")}`}>
          {status}
        </span>
      </div>

      <p className="pollutant-name">{name}</p>

      <h4>
        {value}
        <span>{unit}</span>
      </h4>

      <div className="pollutant-line">
        <div></div>
      </div>
    </div>
  );
}

export default Dashboard;
