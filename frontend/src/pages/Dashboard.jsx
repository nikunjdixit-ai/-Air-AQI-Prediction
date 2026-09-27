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

export function Dashboard({
  navigateTo,
  selectedCity,
  locationMode = "city",
  userCoords = null,
  locationNotice = null,
  onDismissLocationNotice,
  onLocationResolved,
}) {
  const [data, setData] = useState(null);
  const [loadedKey, setLoadedKey] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const lat = userCoords?.lat ?? null;
  const lon = userCoords?.lon ?? null;
  const activeQueryKey =
    locationMode === "current" && lat != null && lon != null
      ? `coords:${lat},${lon}`
      : `city:${selectedCity}`;

  const loading = refreshing || loadedKey !== activeQueryKey;

  useEffect(() => {
    let isCancelled = false;

    const query =
      locationMode === "current" && lat != null && lon != null
        ? { lat, lon, city: selectedCity }
        : selectedCity;

    getLiveAQI(query)
      .then((result) => {
        if (!isCancelled) {
          setData(result);
          setLoadedKey(activeQueryKey);
          if (
            locationMode === "current" &&
            result?.city &&
            typeof onLocationResolved === "function"
          ) {
            onLocationResolved(result.city);
          }
        }
      })
      .catch(() => {
        if (!isCancelled) {
          setLoadedKey(activeQueryKey);
        }
      });

    return () => {
      isCancelled = true;
    };
  }, [selectedCity, locationMode, lat, lon, activeQueryKey, onLocationResolved]);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      const query =
        locationMode === "current" && lat != null && lon != null
          ? { lat, lon, city: selectedCity }
          : selectedCity;
      const result = await getLiveAQI(query);
      setData(result);
      setLoadedKey(activeQueryKey);
      if (
        locationMode === "current" &&
        result?.city &&
        typeof onLocationResolved === "function"
      ) {
        onLocationResolved(result.city);
      }
    } finally {
      setRefreshing(false);
    }
  };

  const isLiveMode = !loading && data?.dataMode === "live" && !data?.isFallback;
  const isOfflineBaseline =
    !loading && (data?.dataMode === "offline_baseline" || data?.isFallback);

  const aqiVal = loading ? "—" : data?.aqi ?? "—";
  const numericAqi = typeof data?.aqi === "number" ? data.aqi : 0;
  const progressPercent = loading
    ? 12
    : Math.min(100, Math.max(8, (numericAqi / 400) * 100));

  const displayLocation =
    data?.city || (selectedCity ? `${selectedCity}, India` : "Kanpur, India");

  return (
    <>
      {/* STATE 4 — LOCATION PERMISSION DENIED / UNAVAILABLE (Non-blocking notice) */}
      {locationNotice && (
        <div
          role="status"
          style={{
            background: "#f0f9ff",
            border: "1px solid #bae6fd",
            color: "#0369a1",
            borderRadius: 12,
            padding: "10px 16px",
            marginBottom: 14,
            fontSize: 12.5,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <span>ℹ️ {locationNotice}</span>
          {onDismissLocationNotice && (
            <button
              onClick={onDismissLocationNotice}
              aria-label="Dismiss location notice"
              style={{
                background: "transparent",
                border: "none",
                color: "#0369a1",
                fontWeight: 700,
                cursor: "pointer",
                fontSize: 14,
                lineHeight: 1,
              }}
            >
              ×
            </button>
          )}
        </div>
      )}

      {/* STATE 2 — LOADING INDICATOR */}
      {loading && (
        <div
          role="status"
          style={{
            background: "#f0fdf4",
            border: "1px solid #bbf7d0",
            color: "#166534",
            borderRadius: 12,
            padding: "10px 16px",
            marginBottom: 16,
            fontSize: 12.5,
            display: "flex",
            alignItems: "center",
            gap: 8,
          }}
        >
          <RefreshCw size={14} className="spin" />
          <span>Fetching live air quality...</span>
        </div>
      )}

      {/* STATE 3 — OFFLINE BASELINE FALLBACK BANNER */}
      {isOfflineBaseline && (
        <div
          role="alert"
          style={{
            background: "#fffbeb",
            border: "1px solid #fde68a",
            color: "#92400e",
            borderRadius: 12,
            padding: "10px 16px",
            marginBottom: 20,
            fontSize: 12.5,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: 12,
          }}
        >
          <span>
            ⚠️ <strong>OFFLINE BASELINE:</strong> Live air-quality data is currently unavailable. Showing a calibrated baseline profile.
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
              whiteSpace: "nowrap",
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
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  marginBottom: 4,
                  flexWrap: "wrap",
                }}
              >
                <p className="label" style={{ margin: 0 }}>
                  CURRENT AIR QUALITY
                </p>

                {/* Explicit Mode Badge: LIVE vs OFFLINE BASELINE vs LOADING */}
                {loading && (
                  <span
                    style={{
                      fontSize: 10.5,
                      fontWeight: 700,
                      padding: "2px 8px",
                      borderRadius: 999,
                      background: "#e2e8f0",
                      color: "#475569",
                      letterSpacing: "0.04em",
                    }}
                  >
                    LOADING...
                  </span>
                )}

                {isLiveMode && (
                  <span
                    style={{
                      fontSize: 10.5,
                      fontWeight: 700,
                      padding: "2px 8px",
                      borderRadius: 999,
                      background: "#dcfce7",
                      color: "#15803d",
                      border: "1px solid #86efac",
                      letterSpacing: "0.04em",
                      display: "inline-flex",
                      alignItems: "center",
                      gap: 5,
                    }}
                  >
                    <span
                      style={{
                        width: 6,
                        height: 6,
                        borderRadius: "50%",
                        background: "#16a34a",
                        display: "inline-block",
                      }}
                    />
                    LIVE
                  </span>
                )}

                {isOfflineBaseline && (
                  <span
                    style={{
                      fontSize: 10.5,
                      fontWeight: 700,
                      padding: "2px 8px",
                      borderRadius: 999,
                      background: "#fef3c7",
                      color: "#b45309",
                      border: "1px solid #fcd34d",
                      letterSpacing: "0.04em",
                    }}
                  >
                    OFFLINE BASELINE
                  </span>
                )}
              </div>
              <h3>Air Quality Index</h3>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <button
                onClick={handleRefresh}
                disabled={loading}
                title="Refresh air quality data"
                style={{
                  background: "rgba(255,255,255,0.7)",
                  border: "1px solid #e2e8f0",
                  borderRadius: 8,
                  padding: "6px 8px",
                  cursor: loading ? "wait" : "pointer",
                  color: "#385249",
                  display: "flex",
                  alignItems: "center",
                }}
              >
                <RefreshCw size={15} />
              </button>
              <div className="aqi-icon">
                <Wind size={24} />
              </div>
            </div>
          </div>

          <div className="aqi-value">
            {loading ? <span style={{ opacity: 0.5 }}>...</span> : aqiVal}
          </div>

          <div className="aqi-status">
            <span
              style={{
                backgroundColor: loading
                  ? "#94a3b8"
                  : data?.categoryColor || "#84cc16",
              }}
            ></span>
            {loading
              ? "Fetching live air quality..."
              : data?.category || "Unavailable"}
          </div>

          <p className="aqi-description">
            {loading
              ? "Connecting to atmospheric monitoring station..."
              : data?.description ||
                "Air quality is acceptable; sensitive individuals may experience minor respiratory irritation."}
          </p>

          {/* Explicit Provenance Metadata Block */}
          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: "8px 16px",
              fontSize: 11.5,
              color: "#475569",
              background: "rgba(255,255,255,0.65)",
              border: "1px solid rgba(148, 163, 184, 0.25)",
              borderRadius: 10,
              padding: "8px 12px",
              marginTop: 10,
              marginBottom: 10,
            }}
          >
            <span>
              <strong>Location:</strong>{" "}
              {loading ? "Resolving..." : displayLocation}
            </span>
            <span>
              <strong>Source:</strong>{" "}
              {loading
                ? "—"
                : isLiveMode
                ? data?.weather?.isFallback
                  ? "Live AQI • Baseline Weather"
                  : "Live Air Quality Data"
                : "Offline City Baseline"}
            </span>
            <span>
              <strong>Updated:</strong>{" "}
              {loading ? "—" : isLiveMode ? data?.timestamp || "—" : "—"}
            </span>
          </div>

          <div className="aqi-bar">
            <div className="bar-background">
              <div
                className="bar-progress"
                style={{
                  width: `${progressPercent}%`,
                  backgroundColor: loading
                    ? "#94a3b8"
                    : data?.categoryColor || "#1f8f63",
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
            value={loading ? "—" : data?.weather?.temperature || "—"}
            description={
              loading
                ? "Fetching live air quality..."
                : data?.weather?.isFallback
                ? "Calibrated city baseline"
                : "Atmospheric condition"
            }
          />

          <InfoCard
            icon={<Droplets size={20} />}
            title="Humidity"
            value={loading ? "—" : data?.weather?.humidity || "—"}
            description={
              data?.weather?.isFallback
                ? "Calibrated baseline"
                : "Relative humidity"
            }
          />

          <InfoCard
            icon={<Wind size={20} />}
            title="Wind Speed"
            value={loading ? "—" : data?.weather?.windSpeed || "—"}
            description={
              data?.weather?.isFallback
                ? "Calibrated baseline"
                : "Ventilation velocity"
            }
          />

          <InfoCard
            icon={<Activity size={20} />}
            title="AQI Trend / Mixing"
            value={loading ? "—" : data?.weather?.trend || "—"}
            description={
              data?.weather?.isFallback
                ? "Baseline dispersion (Live weather offline)"
                : "Atmospheric dispersion index"
            }
          />
        </div>
      </section>

      <section className="section">
        <div className="section-heading">
          <div>
            <p className="label">CURRENT READINGS</p>
            <h3>Pollutant Levels ({displayLocation})</h3>
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
              value={loading ? "—" : p.value}
              unit={p.unit}
              status={loading ? "Loading" : p.status}
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
