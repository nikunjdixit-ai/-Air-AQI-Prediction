import {
  Activity,
  ArrowRight,
  Brain,
  CheckCircle2,
  Database,
  Layers3,
  Server,
} from "lucide-react";
import { MODEL_BENCHMARKS, MODEL_FEATURES } from "../data/mockData";

export function Model({ systemHealth }) {
  const isOnline = systemHealth?.online;
  const modelLoaded = systemHealth?.modelLoaded;

  const pipeline = [
    {
      number: "01",
      title: "Input Acquisition",
      text: "Monitored pollutant concentrations (PM2.5, PM10, NO2, SO2, CO, O3) are gathered via the web form or API payload.",
    },
    {
      number: "02",
      title: "Data Imputation & Preprocessing",
      text: "Secondary trace gases (NO, NOx, NH3, VOCs) and calendar date components are standardized with national median baselines.",
    },
    {
      number: "03",
      title: "Random Forest Ensemble",
      text: "A trained ensemble of decision trees processes the 15-dimensional vector to capture non-linear atmospheric dispersion.",
    },
    {
      number: "04",
      title: "AQI & Health Guidance",
      text: "Continuous AQI index is generated with CPCB category classification, dominant pollutant identification, and health advisories.",
    },
  ];

  return (
    <div className="model-page">
      {/* HERO */}
      <section className="model-hero">
        <div className="model-hero-content">
          <div className="model-hero-icon">
            <Brain size={30} />
          </div>

          <div>
            <div className="model-status">
              <span></span>
              {isOnline && modelLoaded ? "Production Model Online" : "Model Initialized"}
            </div>

            <h3>AQI Prediction Model Architecture</h3>

            <p>
              An ensemble machine learning pipeline trained on multi-year Indian urban
              air quality datasets to deliver robust, non-linear AQI forecasting.
            </p>
          </div>
        </div>

        <div className="model-hero-side">
          <span>MODEL ENGINE</span>
          <strong>Tuned Random Forest</strong>
          <small>
            {isOnline ? "Render Flask API Connected" : "Local Standby Mode"}
          </small>
        </div>
      </section>

      {/* MODEL OVERVIEW */}
      <section className="model-overview">
        <div className="model-info-card">
          <div className="model-info-icon">
            <Database size={21} />
          </div>
          <div>
            <span>Input Dimensions</span>
            <strong>15 Features</strong>
            <small>6 User + 9 Auto-Imputed</small>
          </div>
        </div>

        <div className="model-info-card">
          <div className="model-info-icon">
            <Layers3 size={21} />
          </div>
          <div>
            <span>Target Output</span>
            <strong>AQI Index</strong>
            <small>Continuous numeric scale</small>
          </div>
        </div>

        <div className="model-info-card">
          <div className="model-info-icon">
            <Server size={21} />
          </div>
          <div>
            <span>REST API</span>
            <strong>{isOnline ? "Active" : "Ready"}</strong>
            <small>{isOnline ? "Render Deployment" : "Standing By"}</small>
          </div>
        </div>

        <div className="model-info-card">
          <div className="model-info-icon">
            <CheckCircle2 size={21} />
          </div>
          <div>
            <span>Serialization</span>
            <strong>Joblib Pipeline</strong>
            <small>models/best_model.pkl</small>
          </div>
        </div>
      </section>

      {/* MODEL BENCHMARKS & EVALUATION */}
      <section className="model-section">
        <div className="model-section-heading">
          <div>
            <p className="label">EMPIRICAL BENCHMARKS</p>
            <h3>Model Evaluation &amp; Comparison</h3>
            <p>
              Benchmarked against 4 candidate architectures evaluated on holdout test splits
              from the historical Indian CPCB air quality dataset.
            </p>
          </div>
          <div className="feature-count">Best: R² = 0.8877</div>
        </div>

        <div className="metrics-grid">
          <div className="metric-card">
            <span>R² Score (Variance Explained)</span>
            <strong style={{ color: "#15803d" }}>0.8877</strong>
            <small>88.77% test variance fit</small>
          </div>

          <div className="metric-card">
            <span>Mean Absolute Error (MAE)</span>
            <strong style={{ color: "#15803d" }}>20.22</strong>
            <small>Average AQI error margin</small>
          </div>

          <div className="metric-card">
            <span>Root Mean Squared Error (RMSE)</span>
            <strong style={{ color: "#15803d" }}>41.85</strong>
            <small>Penalizes outlier predictions</small>
          </div>

          <div className="metric-card">
            <span>Production Version</span>
            <strong style={{ color: "#0c2118" }}>v1.1.0</strong>
            <small>Serialized Scikit-Learn Pipeline</small>
          </div>
        </div>

        {/* Benchmark Table */}
        <div style={{ marginTop: 24, overflowX: "auto" }}>
          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
              fontSize: 12,
              textAlign: "left",
            }}
          >
            <thead>
              <tr style={{ borderBottom: "2px solid #e1e9e4", color: "#61756a" }}>
                <th style={{ padding: "10px 14px" }}>Candidate Model</th>
                <th style={{ padding: "10px 14px" }}>Architecture</th>
                <th style={{ padding: "10px 14px" }}>MAE</th>
                <th style={{ padding: "10px 14px" }}>RMSE</th>
                <th style={{ padding: "10px 14px" }}>R² Score</th>
                <th style={{ padding: "10px 14px" }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {MODEL_BENCHMARKS.map((m) => (
                <tr
                  key={m.model}
                  style={{
                    borderBottom: "1px solid #e8edea",
                    background: m.isBest ? "#f3f8ee" : "transparent",
                    fontWeight: m.isBest ? 600 : 400,
                  }}
                >
                  <td style={{ padding: "12px 14px" }}>{m.model}</td>
                  <td style={{ padding: "12px 14px", color: "#71847b" }}>{m.badge}</td>
                  <td style={{ padding: "12px 14px" }}>{m.mae}</td>
                  <td style={{ padding: "12px 14px" }}>{m.rmse}</td>
                  <td style={{ padding: "12px 14px", color: m.isBest ? "#15803d" : "inherit" }}>
                    {m.r2.toFixed(4)}
                  </td>
                  <td style={{ padding: "12px 14px" }}>
                    <span
                      style={{
                        padding: "3px 8px",
                        borderRadius: 12,
                        fontSize: 10,
                        fontWeight: 700,
                        background: m.isBest ? "#c6f36b" : "#e8edea",
                        color: m.isBest ? "#10251b" : "#61756a",
                      }}
                    >
                      {m.isBest ? "Deployed" : "Evaluated"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* INPUT FEATURES (15-FEATURE MATRIX) */}
      <section className="model-section">
        <div className="model-section-heading">
          <div>
            <p className="label">FEATURE MATRIX</p>
            <h3>All 15 Pipeline Features</h3>
            <p>
              The model accepts 6 direct user inputs and automatically fills remaining
              features to prevent input friction while preserving high dimensional accuracy.
            </p>
          </div>
          <div className="feature-count">15 Features Total</div>
        </div>

        <div className="feature-grid">
          {MODEL_FEATURES.map((feature) => (
            <div className="feature-card" key={feature.name}>
              <div className="feature-icon">
                <Activity size={17} />
              </div>
              <div style={{ flex: 1 }}>
                <strong>{feature.name}</strong>
                <span>{feature.description}</span>
                <span
                  style={{
                    display: "inline-block",
                    marginTop: 3,
                    fontSize: 8.5,
                    fontWeight: 700,
                    color: feature.source.startsWith("Direct") ? "#15803d" : "#71847b",
                  }}
                >
                  {feature.source}
                </span>
              </div>
              <CheckCircle2 size={17} className="feature-check" />
            </div>
          ))}
        </div>
      </section>

      {/* WORKFLOW PIPELINE */}
      <section className="model-section">
        <div className="model-section-heading">
          <div>
            <p className="label">PREDICTION PIPELINE</p>
            <h3>Inference Lifecycle</h3>
            <p>From web input payload to calibrated AQI score and health guidance.</p>
          </div>
        </div>

        <div className="pipeline">
          {pipeline.map((step, index) => (
            <div className="pipeline-step" key={step.number}>
              <div className="pipeline-number">{step.number}</div>
              <div className="pipeline-content">
                <h4>{step.title}</h4>
                <p>{step.text}</p>
              </div>
              {index < pipeline.length - 1 && (
                <ArrowRight className="pipeline-arrow" size={19} />
              )}
            </div>
          ))}
        </div>
      </section>

      {/* BACKEND INTEGRATION CARD */}
      <section className="integration-card">
        <div className="integration-icon">
          <Server size={23} />
        </div>

        <div className="integration-content">
          <p className="label">BACKEND INTEGRATION STATUS</p>
          <h3>
            {isOnline
              ? "Flask REST API & Production Model Active"
              : "Connecting to Flask API & WSGI Server"}
          </h3>
          <p>
            {isOnline
              ? `AirSense is actively communicating with the backend (Render / Gunicorn). Model weights (models/best_model.pkl) are verified and serving inference at /predict.`
              : `The frontend is configured to target https://air-aqi-prediction.onrender.com. When running locally, start app.py on port 5000.`}
          </p>
        </div>

        <div className="integration-status">
          <span
            style={{
              backgroundColor: isOnline ? "#15803d" : "#e0a23c",
            }}
          ></span>
          {isOnline ? "Connected & Healthy" : "Offline / Connecting"}
        </div>
      </section>
    </div>
  );
}

export default Model;
