import { useState } from "react";
import {
  Activity,
  ArrowRight,
  Brain,
  Info,
  RotateCcw,
  Sparkles,
} from "lucide-react";
import { predictAQI } from "../services/aqiService";

export function Prediction({ selectedCity = "Delhi" }) {
  const [formData, setFormData] = useState({
    pm25: "",
    pm10: "",
    no2: "",
    so2: "",
    co: "",
    o3: "",
  });

  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (field, value) => {
    setFormData((previous) => ({
      ...previous,
      [field]: value,
    }));
    setError("");
  };

  const loadSampleData = () => {
    setFormData({
      pm25: "58.5",
      pm10: "112.0",
      no2: "34.2",
      so2: "14.1",
      co: "1.2",
      o3: "45.0",
    });
    setPrediction(null);
    setError("");
  };

  const clearForm = () => {
    setFormData({
      pm25: "",
      pm10: "",
      no2: "",
      so2: "",
      co: "",
      o3: "",
    });
    setPrediction(null);
    setError("");
  };

  const handlePrediction = async (event) => {
    event.preventDefault();

    // Verify at least one pollutant is provided
    const enteredValues = Object.entries(formData).filter(
      ([, val]) => val !== "" && val !== null && !isNaN(Number(val))
    );

    if (enteredValues.length === 0) {
      setError("Please enter at least one valid pollutant concentration.");
      return;
    }

    // Verify no negative values
    for (const [key, val] of enteredValues) {
      if (Number(val) < 0) {
        setError(`Concentration for ${key.toUpperCase()} cannot be negative.`);
        return;
      }
    }

    setLoading(true);
    setError("");

    try {
      const result = await predictAQI(formData, selectedCity, "today");
      setPrediction(result);
    } catch (err) {
      setError(err.message || "Prediction failed. Verify that backend is running.");
      setPrediction(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="prediction-page">
      <div className="form-card">
        <div className="prediction-title-row">
          <div>
            <p className="label">MACHINE LEARNING PREDICTION</p>
            <h3>Enter Air Quality Data ({selectedCity})</h3>
          </div>

          <div className="prediction-icon">
            <Sparkles size={22} />
          </div>
        </div>

        <p className="form-description">
          Enter monitored pollutant concentrations. Unspecified trace parameters
          (NO, NOx, NH3, VOCs, Calendar) are automatically imputed by the backend pipeline.
        </p>

        <form onSubmit={handlePrediction}>
          <div className="form-grid">
            <Input
              label="PM2.5"
              unit="µg/m³"
              placeholder="e.g. 58.5"
              value={formData.pm25}
              onChange={(value) => handleChange("pm25", value)}
            />

            <Input
              label="PM10"
              unit="µg/m³"
              placeholder="e.g. 112.0"
              value={formData.pm10}
              onChange={(value) => handleChange("pm10", value)}
            />

            <Input
              label="NO₂"
              unit="µg/m³"
              placeholder="e.g. 34.2"
              value={formData.no2}
              onChange={(value) => handleChange("no2", value)}
            />

            <Input
              label="SO₂"
              unit="µg/m³"
              placeholder="e.g. 14.1"
              value={formData.so2}
              onChange={(value) => handleChange("so2", value)}
            />

            <Input
              label="CO"
              unit="mg/m³"
              placeholder="e.g. 1.2"
              value={formData.co}
              onChange={(value) => handleChange("co", value)}
            />

            <Input
              label="O₃"
              unit="µg/m³"
              placeholder="e.g. 45.0"
              value={formData.o3}
              onChange={(value) => handleChange("o3", value)}
            />
          </div>

          {error && <div className="form-error">{error}</div>}

          <div className="form-actions">
            <button
              type="button"
              className="secondary-button"
              onClick={loadSampleData}
              disabled={loading}
            >
              <Sparkles size={16} />
              Load Sample
            </button>

            <button
              type="button"
              className="secondary-button"
              onClick={clearForm}
              disabled={loading}
            >
              <RotateCcw size={16} />
              Clear
            </button>

            <button
              type="submit"
              className="primary-button predict-button"
              disabled={loading}
            >
              {loading ? (
                <span>Computing Forecast...</span>
              ) : (
                <>
                  <Activity size={18} />
                  Predict AQI
                  <ArrowRight size={16} />
                </>
              )}
            </button>
          </div>
        </form>

        {/* Feature Imputation Transparency Notice */}
        <div
          style={{
            marginTop: 22,
            padding: "12px 14px",
            borderRadius: 10,
            background: "#f3f7f4",
            border: "1px solid #dce7df",
            fontSize: 11,
            color: "#4f695d",
            display: "flex",
            alignItems: "flex-start",
            gap: 8,
            lineHeight: 1.5,
          }}
        >
          <Info size={16} style={{ flexShrink: 0, marginTop: 1, color: "#1f8f63" }} />
          <span>
            <strong>15-Feature Model Architecture:</strong> You enter up to 6 primary pollutants. The remaining 9 parameters (NO, NOx, NH3, Benzene, Toluene, Xylene, Year, Month, Day) are filled by the Scikit-Learn pipeline from historical Indian urban medians.
          </span>
        </div>
      </div>

      <div className="prediction-result">
        <div className="result-icon">
          <Brain size={25} />
        </div>

        <p className="label">PREDICTION RESULT</p>

        {!prediction && !loading && (
          <>
            <div className="result-number">—</div>
            <h3>Awaiting Prediction</h3>
            <p>
              Enter pollutant levels and click <strong>Predict AQI</strong> to
              execute the Random Forest inference engine.
            </p>
          </>
        )}

        {loading && (
          <div style={{ textAlign: "center", padding: "40px 10px" }}>
            <div
              style={{
                width: 32,
                height: 32,
                border: "3px solid #dce5df",
                borderTopColor: "#1f8f63",
                borderRadius: "50%",
                animation: "spin 0.8s linear infinite",
                margin: "0 auto 16px",
              }}
            ></div>
            <p style={{ color: "#71847b", fontSize: 13 }}>
              Executing Random Forest Pipeline...
            </p>
          </div>
        )}

        {prediction && !loading && (
          <>
            <div
              className="result-number"
              style={{
                color: prediction.categoryColor || "#10251b",
                transition: "color 0.3s ease",
              }}
            >
              {prediction.roundedAqi}
            </div>

            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 6,
                padding: "6px 14px",
                borderRadius: 20,
                background: prediction.categoryBg || "#edf7df",
                color: prediction.categoryColor || "#5e8039",
                fontWeight: 700,
                fontSize: 12,
                marginTop: 6,
              }}
            >
              <span
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: "50%",
                  backgroundColor: prediction.categoryColor || "#5e8039",
                }}
              ></span>
              {prediction.category}
            </div>

            <h3 style={{ marginTop: 14 }}>
              Dominant Driver: {prediction.dominantPollutant}
            </h3>

            <p style={{ fontSize: 12, lineHeight: 1.5, color: "#61756a" }}>
              {prediction.healthMessage}
            </p>

            {/* Factor contributions breakdown */}
            {prediction.factorContributions && prediction.factorContributions.length > 0 && (
              <div style={{ marginTop: 18, borderTop: "1px solid #e3eae5", paddingTop: 14 }}>
                <span style={{ fontSize: 11, fontWeight: 700, color: "#71847b", letterSpacing: 0.5 }}>
                  POLLUTANT IMPACT FACTORS
                </span>
                <div style={{ display: "grid", gap: 6, marginTop: 8 }}>
                  {prediction.factorContributions.slice(0, 4).map((f) => (
                    <div key={f.pollutant} style={{ fontSize: 11 }}>
                      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 2 }}>
                        <span style={{ fontWeight: 600 }}>{f.pollutant}</span>
                        <span style={{ color: "#71847b" }}>{f.percentage}% impact</span>
                      </div>
                      <div style={{ height: 5, background: "#e8edea", borderRadius: 3, overflow: "hidden" }}>
                        <div
                          style={{
                            width: `${Math.min(100, f.percentage)}%`,
                            height: "100%",
                            background: f.is_dominant ? "#1f8f63" : "#7bb38e",
                            borderRadius: 3,
                          }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}

        <div className="result-info">
          <div>
            <span>Model Engine</span>
            <strong>Random Forest</strong>
          </div>

          <div>
            <span>Feature Pipeline</span>
            <strong>15 Features</strong>
          </div>

          <div>
            <span>Status</span>
            <strong style={{ color: prediction ? "#15803d" : "#71847b" }}>
              {prediction ? "Inference Complete" : "Standby"}
            </strong>
          </div>
        </div>
      </div>
    </div>
  );
}

function Input({ label, unit, placeholder, value, onChange }) {
  return (
    <div className="input-group">
      <div className="input-label-row">
        <label>{label}</label>
        <span>{unit}</span>
      </div>

      <input
        type="number"
        step="any"
        min="0"
        placeholder={placeholder}
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
    </div>
  );
}

export default Prediction;
