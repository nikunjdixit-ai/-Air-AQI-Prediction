import { useEffect, useState } from "react";
import {
  Activity,
  Calendar,
  TrendingDown,
  TrendingUp,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { CITY_DEFAULTS, getCategoryInfo } from "../data/mockData";
import { getHistoricalAQI } from "../services/aqiService";

export function Analytics({ selectedCity = "Delhi" }) {
  const [historicalData, setHistoricalData] = useState(null);
  const cityProfile = CITY_DEFAULTS[selectedCity] || CITY_DEFAULTS["Delhi"];

  // Weekly data from city defaults
  const aqiData = cityProfile.weeklyTrend || [];
  const pollutantData = cityProfile.pollutants || [];

  useEffect(() => {
    let isMounted = true;
    getHistoricalAQI(selectedCity).then((data) => {
      if (isMounted && data) {
        setHistoricalData(data);
      }
    });
    return () => {
      isMounted = false;
    };
  }, [selectedCity]);

  // Dynamic stats
  const aqiValues = aqiData.map((d) => d.aqi);
  const avgAqi = aqiValues.length
    ? Math.round(aqiValues.reduce((a, b) => a + b, 0) / aqiValues.length)
    : 144;
  const maxAqi = aqiValues.length ? Math.max(...aqiValues) : 158;
  const minAqi = aqiValues.length ? Math.min(...aqiValues) : 128;

  // Compute dynamic domain for Recharts line chart
  const yMin = Math.max(0, Math.floor(minAqi * 0.85));
  const yMax = Math.ceil(maxAqi * 1.15);

  return (
    <div className="analytics-page">
      <div className="analytics-stats">
        <div className="analytics-stat-card">
          <div className="stat-icon">
            <Activity size={20} />
          </div>
          <div>
            <span>Average AQI ({selectedCity})</span>
            <strong>{avgAqi}</strong>
            <small>7-day moving average</small>
          </div>
        </div>

        <div className="analytics-stat-card">
          <div className="stat-icon">
            <TrendingUp size={20} />
          </div>
          <div>
            <span>Highest AQI</span>
            <strong>{maxAqi}</strong>
            <small>{getCategoryInfo(maxAqi).name} tier</small>
          </div>
        </div>

        <div className="analytics-stat-card">
          <div className="stat-icon">
            <TrendingDown size={20} />
          </div>
          <div>
            <span>Lowest AQI</span>
            <strong>{minAqi}</strong>
            <small>{getCategoryInfo(minAqi).name} tier</small>
          </div>
        </div>
      </div>

      {/* 7-Day Trend Chart */}
      <div className="analytics-card">
        <div className="analytics-heading">
          <div>
            <p className="label">AIR QUALITY TREND</p>
            <h3>7-Day AQI Overview — {selectedCity}</h3>
          </div>
          <div className="chart-badge">Weekly Trend</div>
        </div>

        <div className="chart-container">
          <ResponsiveContainer width="100%" height={320}>
            <LineChart
              data={aqiData}
              margin={{ top: 15, right: 25, left: 5, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2ece6" />
              <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fill: "#607369", fontSize: 12 }} />
              <YAxis
                domain={[yMin, yMax]}
                axisLine={false}
                tickLine={false}
                tick={{ fill: "#607369", fontSize: 12 }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#08271c",
                  border: "none",
                  borderRadius: "10px",
                  color: "#fff",
                  fontSize: "12px",
                }}
                formatter={(val) => [`${val} AQI (${getCategoryInfo(val).name})`, "Air Quality"]}
              />
              <Line
                type="monotone"
                dataKey="aqi"
                stroke="#1f8f63"
                strokeWidth={3}
                dot={{ r: 5, fill: "#1f8f63" }}
                activeDot={{ r: 8, fill: "#c6f36b" }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Pollutant Breakdown BarChart */}
      <div className="analytics-card">
        <div className="analytics-heading">
          <div>
            <p className="label">POLLUTANT CONCENTRATIONS</p>
            <h3>Current Pollutant Spectrum ({selectedCity})</h3>
          </div>
          <div className="chart-badge">Particulate &amp; Gas</div>
        </div>

        <div className="chart-container">
          <ResponsiveContainer width="100%" height={320}>
            <BarChart
              data={pollutantData}
              margin={{ top: 15, right: 25, left: 5, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2ece6" />
              <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: "#607369", fontSize: 12 }} />
              <YAxis axisLine={false} tickLine={false} tick={{ fill: "#607369", fontSize: 12 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#08271c",
                  border: "none",
                  borderRadius: "10px",
                  color: "#fff",
                  fontSize: "12px",
                }}
                formatter={(value, name, item) => [
                  `${value} ${item.payload.unit || "µg/m³"}`,
                  item.payload.name,
                ]}
              />
              <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                {pollutantData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={entry.name.startsWith("PM") ? "#1f8f63" : "#4fa682"}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Historical Distribution & Seasonal Insights */}
      {historicalData?.seasonal_averages && (
        <div
          className="analytics-card"
          style={{
            background: "#fbfdfa",
            border: "1px solid #dce5df",
          }}
        >
          <div className="analytics-heading">
            <div>
              <p className="label">MULTI-YEAR HISTORICAL BENCHMARK</p>
              <h3>Seasonal Distribution Profile ({historicalData.matched_historical_dataset})</h3>
            </div>
            <div className="chart-badge">
              <Calendar size={11} style={{ marginRight: 4 }} />
              {historicalData.date_range_covered}
            </div>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
              gap: 16,
              marginTop: 10,
            }}
          >
            <div style={{ padding: 16, background: "white", borderRadius: 12, border: "1px solid #e2ece6" }}>
              <span style={{ fontSize: 11, color: "#71847b" }}>Winter Average (Nov–Jan)</span>
              <h4 style={{ fontSize: 22, marginTop: 4, color: "#b91c1c" }}>
                {historicalData.seasonal_averages.winter_nov_jan} AQI
              </h4>
              <p style={{ fontSize: 11, color: "#9aa8a2", marginTop: 4 }}>
                Inversion &amp; biomass stagnation
              </p>
            </div>

            <div style={{ padding: 16, background: "white", borderRadius: 12, border: "1px solid #e2ece6" }}>
              <span style={{ fontSize: 11, color: "#71847b" }}>Monsoon Average (Jul–Sep)</span>
              <h4 style={{ fontSize: 22, marginTop: 4, color: "#15803d" }}>
                {historicalData.seasonal_averages.monsoon_jul_sep} AQI
              </h4>
              <p style={{ fontSize: 11, color: "#9aa8a2", marginTop: 4 }}>
                Precipitation wet-scavenging
              </p>
            </div>

            <div style={{ padding: 16, background: "white", borderRadius: 12, border: "1px solid #e2ece6" }}>
              <span style={{ fontSize: 11, color: "#71847b" }}>Summer Average (Apr–Jun)</span>
              <h4 style={{ fontSize: 22, marginTop: 4, color: "#a16207" }}>
                {historicalData.seasonal_averages.summer_apr_jun} AQI
              </h4>
              <p style={{ fontSize: 11, color: "#9aa8a2", marginTop: 4 }}>
                Convective thermal dispersion
              </p>
            </div>

            <div style={{ padding: 16, background: "white", borderRadius: 12, border: "1px solid #e2ece6" }}>
              <span style={{ fontSize: 11, color: "#71847b" }}>Total Historical Records</span>
              <h4 style={{ fontSize: 22, marginTop: 4, color: "#10231c" }}>
                {historicalData.records_count?.toLocaleString()} Days
              </h4>
              <p style={{ fontSize: 11, color: "#9aa8a2", marginTop: 4 }}>
                Median: {historicalData.stats?.median_aqi} AQI
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Analytics;
