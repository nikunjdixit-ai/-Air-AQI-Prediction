import { useState } from "react";
import "./App.css";

import {
  Activity,
  BarChart3,
  Brain,
  Cloud,
  Database,
  Droplets,
  LayoutDashboard,
  Menu,
  Wind,
  X,
  ArrowRight,
  RotateCcw,
  Sparkles,
  TrendingUp,
  TrendingDown,
  CheckCircle2,
  Layers3,
  Server,
} from "lucide-react";

import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const aqiData = [
  { day: "Mon", aqi: 128 },
  { day: "Tue", aqi: 136 },
  { day: "Wed", aqi: 151 },
  { day: "Thu", aqi: 145 },
  { day: "Fri", aqi: 158 },
  { day: "Sat", aqi: 149 },
  { day: "Sun", aqi: 142 },
];

const pollutantData = [
  { name: "PM2.5", value: 48.2 },
  { name: "PM10", value: 82.5 },
  { name: "NO₂", value: 31.4 },
  { name: "SO₂", value: 12.8 },
  { name: "CO", value: 0.8 },
  { name: "O₃", value: 42.1 },
];

function App() {
  const [activePage, setActivePage] = useState("dashboard");
  const [menuOpen, setMenuOpen] = useState(false);

  const navItems = [
    { id: "dashboard", name: "Dashboard", icon: LayoutDashboard },
    { id: "predict", name: "Predict AQI", icon: Activity },
    { id: "analytics", name: "Analytics", icon: BarChart3 },
    { id: "model", name: "ML Model", icon: Brain },
  ];

  const navigateTo = (page) => {
    setActivePage(page);
    setMenuOpen(false);
  };

  return (
    <div className="app">
      <aside className={`sidebar ${menuOpen ? "open" : ""}`}>
        <div className="logo">
          <div className="logo-icon">
            <Wind size={24} />
          </div>

          <div>
            <h1>AirSense</h1>
            <p>AQI Prediction</p>
          </div>
        </div>

        <nav>
          {navItems.map((item) => {
            const Icon = item.icon;

            return (
              <button
                key={item.id}
                className={`nav-item ${
                  activePage === item.id ? "active" : ""
                }`}
                onClick={() => navigateTo(item.id)}
              >
                <Icon size={19} />
                <span>{item.name}</span>
              </button>
            );
          })}
        </nav>

        <div className="sidebar-bottom">
          <div className="online-dot"></div>

          <div>
            <strong>ML System</strong>
            <span>Ready for prediction</span>
          </div>
        </div>
      </aside>

      <button
        className="mobile-menu"
        onClick={() => setMenuOpen(!menuOpen)}
      >
        {menuOpen ? <X /> : <Menu />}
      </button>

      <main className="main">
        <header className="header">
          <div>
            <p className="small-title">AIR QUALITY INTELLIGENCE</p>

            <h2>
              {activePage === "dashboard" && "Air Quality Dashboard"}
              {activePage === "predict" && "Predict AQI"}
              {activePage === "analytics" && "Air Quality Analytics"}
              {activePage === "model" && "Machine Learning Model"}
            </h2>

            <p className="subtitle">
              Monitor, analyze and predict air quality using machine learning.
            </p>
          </div>

          <div className="location">
            <span className="location-dot"></span>
            Kanpur, India
          </div>
        </header>

        {activePage === "dashboard" && (
          <Dashboard navigateTo={navigateTo} />
        )}

        {activePage === "predict" && <Prediction />}

        {activePage === "analytics" && <Analytics />}

        {activePage === "model" && <Model />}
      </main>
    </div>
  );
}


/* =====================================================
   DASHBOARD
===================================================== */

function Dashboard({ navigateTo }) {
  return (
    <>
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

          <div className="aqi-value">142</div>

          <div className="aqi-status">
            <span></span>
            Moderate
          </div>

          <p className="aqi-description">
            Air quality is acceptable, but sensitive people may experience
            some effects.
          </p>

          <div className="aqi-bar">
            <div className="bar-background">
              <div className="bar-progress"></div>
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
            value="28°C"
            description="Feels like 30°C"
          />

          <InfoCard
            icon={<Droplets size={20} />}
            title="Humidity"
            value="64%"
            description="Normal range"
          />

          <InfoCard
            icon={<Wind size={20} />}
            title="Wind Speed"
            value="8.4 km/h"
            description="Light breeze"
          />

          <InfoCard
            icon={<Activity size={20} />}
            title="AQI Trend"
            value="+4.2%"
            description="Compared to yesterday"
          />
        </div>
      </section>

      <section className="section">
        <div className="section-heading">
          <div>
            <p className="label">CURRENT READINGS</p>
            <h3>Pollutant Levels</h3>
          </div>

          <button
            className="view-button"
            onClick={() => navigateTo("analytics")}
          >
            View analytics →
          </button>
        </div>

        <div className="pollutant-grid">
          <Pollutant
            name="PM2.5"
            value="48.2"
            unit="µg/m³"
            status="Moderate"
          />

          <Pollutant
            name="PM10"
            value="82.5"
            unit="µg/m³"
            status="Moderate"
          />

          <Pollutant
            name="NO₂"
            value="31.4"
            unit="µg/m³"
            status="Good"
          />

          <Pollutant
            name="SO₂"
            value="12.8"
            unit="µg/m³"
            status="Good"
          />

          <Pollutant
            name="CO"
            value="0.8"
            unit="mg/m³"
            status="Good"
          />

          <Pollutant
            name="O₃"
            value="42.1"
            unit="µg/m³"
            status="Good"
          />
        </div>
      </section>

      <section className="prediction-banner">
        <div>
          <p className="label">MACHINE LEARNING</p>

          <h3>Predict the next AQI value</h3>

          <p>
            Use pollutant and environmental data to generate an AQI prediction
            with the trained ML model.
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


/* =====================================================
   SMALL COMPONENTS
===================================================== */

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

        <span className={`status ${status.toLowerCase()}`}>
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


/* =====================================================
   PREDICTION
===================================================== */

function Prediction() {
  const [formData, setFormData] = useState({
    pm25: "",
    pm10: "",
    no2: "",
    so2: "",
    co: "",
    o3: "",
  });

  const [prediction, setPrediction] = useState(null);
  const [error, setError] = useState("");

  const handleChange = (field, value) => {
    setFormData((previous) => ({
      ...previous,
      [field]: value,
    }));

    setError("");
    setPrediction(null);
  };

  const loadSampleData = () => {
    setFormData({
      pm25: "48.2",
      pm10: "82.5",
      no2: "31.4",
      so2: "12.8",
      co: "0.8",
      o3: "42.1",
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

  const handlePrediction = (event) => {
    event.preventDefault();

    const values = Object.values(formData);

    const hasEmptyValue = values.some(
      (value) => value === ""
    );

    if (hasEmptyValue) {
      setError(
        "Please enter values for all pollutants before predicting."
      );

      setPrediction(null);
      return;
    }

    setPrediction({ status: "ready" });
    setError("");
  };

  return (
    <div className="prediction-page">
      <div className="form-card">
        <div className="prediction-title-row">
          <div>
            <p className="label">MACHINE LEARNING PREDICTION</p>

            <h3>Enter Air Quality Data</h3>
          </div>

          <div className="prediction-icon">
            <Sparkles size={22} />
          </div>
        </div>

        <p className="form-description">
          Enter the current pollutant concentrations to generate an AQI
          prediction using the trained machine learning model.
        </p>

        <form onSubmit={handlePrediction}>
          <div className="form-grid">
            <Input
              label="PM2.5"
              unit="µg/m³"
              placeholder="e.g. 48.2"
              value={formData.pm25}
              onChange={(value) =>
                handleChange("pm25", value)
              }
            />

            <Input
              label="PM10"
              unit="µg/m³"
              placeholder="e.g. 82.5"
              value={formData.pm10}
              onChange={(value) =>
                handleChange("pm10", value)
              }
            />

            <Input
              label="NO₂"
              unit="µg/m³"
              placeholder="e.g. 31.4"
              value={formData.no2}
              onChange={(value) =>
                handleChange("no2", value)
              }
            />

            <Input
              label="SO₂"
              unit="µg/m³"
              placeholder="e.g. 12.8"
              value={formData.so2}
              onChange={(value) =>
                handleChange("so2", value)
              }
            />

            <Input
              label="CO"
              unit="mg/m³"
              placeholder="e.g. 0.8"
              value={formData.co}
              onChange={(value) =>
                handleChange("co", value)
              }
            />

            <Input
              label="O₃"
              unit="µg/m³"
              placeholder="e.g. 42.1"
              value={formData.o3}
              onChange={(value) =>
                handleChange("o3", value)
              }
            />
          </div>

          {error && (
            <div className="form-error">
              {error}
            </div>
          )}

          <div className="form-actions">
            <button
              type="button"
              className="secondary-button"
              onClick={loadSampleData}
            >
              <Sparkles size={16} />
              Load Sample
            </button>

            <button
              type="button"
              className="secondary-button"
              onClick={clearForm}
            >
              <RotateCcw size={16} />
              Clear
            </button>

            <button
              type="submit"
              className="primary-button predict-button"
            >
              <Activity size={18} />
              Predict AQI
              <ArrowRight size={16} />
            </button>
          </div>
        </form>
      </div>

      <div className="prediction-result">
        <div className="result-icon">
          <Brain size={25} />
        </div>

        <p className="label">PREDICTION RESULT</p>

        {!prediction ? (
          <>
            <div className="result-number">—</div>

            <h3>Awaiting prediction</h3>

            <p>
              Enter the pollutant values and run the ML model
              to see the predicted AQI.
            </p>
          </>
        ) : (
          <>
            <div className="result-ready">READY</div>

            <h3>Backend connection required</h3>

            <p>
              Your frontend form is working correctly. The actual
              AQI value will appear here after the backend ML API
              is connected.
            </p>
          </>
        )}

        <div className="result-info">
          <div>
            <span>Pollutants</span>
            <strong>6 inputs</strong>
          </div>

          <div>
            <span>Model</span>
            <strong>ML based</strong>
          </div>

          <div>
            <span>Status</span>
            <strong>Ready</strong>
          </div>
        </div>
      </div>
    </div>
  );
}

function Input({
  label,
  unit,
  placeholder,
  value,
  onChange,
}) {
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
        onChange={(event) =>
          onChange(event.target.value)
        }
      />
    </div>
  );
}


/* =====================================================
   ANALYTICS
===================================================== */

function Analytics() {
  return (
    <div className="analytics-page">
      <div className="analytics-stats">
        <div className="analytics-stat-card">
          <div className="stat-icon">
            <Activity size={20} />
          </div>

          <div>
            <span>Average AQI</span>
            <strong>144</strong>
            <small>Last 7 days</small>
          </div>
        </div>

        <div className="analytics-stat-card">
          <div className="stat-icon">
            <TrendingUp size={20} />
          </div>

          <div>
            <span>Highest AQI</span>
            <strong>158</strong>
            <small>Friday</small>
          </div>
        </div>

        <div className="analytics-stat-card">
          <div className="stat-icon">
            <TrendingDown size={20} />
          </div>

          <div>
            <span>Lowest AQI</span>
            <strong>128</strong>
            <small>Monday</small>
          </div>
        </div>
      </div>

      <div className="analytics-card">
        <div className="analytics-heading">
          <div>
            <p className="label">AIR QUALITY TREND</p>
            <h3>7 Day AQI Overview</h3>
          </div>

          <div className="chart-badge">Weekly</div>
        </div>

        <div className="chart-container">
          <ResponsiveContainer width="100%" height={320}>
            <LineChart
              data={aqiData}
              margin={{
                top: 15,
                right: 20,
                left: 0,
                bottom: 5,
              }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                vertical={false}
              />

              <XAxis
                dataKey="day"
                axisLine={false}
                tickLine={false}
              />

              <YAxis
                axisLine={false}
                tickLine={false}
                domain={[100, 180]}
              />

              <Tooltip />

              <Line
                type="monotone"
                dataKey="aqi"
                stroke="#1f8f63"
                strokeWidth={3}
                dot={{ r: 5 }}
                activeDot={{ r: 7 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="analytics-card">
        <div className="analytics-heading">
          <div>
            <p className="label">POLLUTANT ANALYSIS</p>
            <h3>Current Pollutant Levels</h3>
          </div>
        </div>

        <div className="chart-container">
          <ResponsiveContainer width="100%" height={320}>
            <BarChart
              data={pollutantData}
              margin={{
                top: 15,
                right: 20,
                left: 0,
                bottom: 5,
              }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                vertical={false}
              />

              <XAxis
                dataKey="name"
                axisLine={false}
                tickLine={false}
              />

              <YAxis
                axisLine={false}
                tickLine={false}
              />

              <Tooltip />

              <Bar
                dataKey="value"
                fill="#2b9b70"
                radius={[6, 6, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}


/* =====================================================
   ML MODEL PAGE
===================================================== */

function Model() {
  const features = [
    {
      name: "PM2.5",
      description: "Fine particulate matter",
    },
    {
      name: "PM10",
      description: "Coarse particulate matter",
    },
    {
      name: "NO₂",
      description: "Nitrogen dioxide",
    },
    {
      name: "SO₂",
      description: "Sulfur dioxide",
    },
    {
      name: "CO",
      description: "Carbon monoxide",
    },
    {
      name: "O₃",
      description: "Ozone",
    },
  ];

  const pipeline = [
    {
      number: "01",
      title: "Input Data",
      text: "Pollutant and environmental readings are provided to the prediction system.",
    },
    {
      number: "02",
      title: "Preprocessing",
      text: "Input data is prepared in the format required by the trained model.",
    },
    {
      number: "03",
      title: "ML Model",
      text: "The trained machine learning model processes the prepared features.",
    },
    {
      number: "04",
      title: "AQI Prediction",
      text: "The predicted AQI value is returned for frontend visualization.",
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
              Frontend Ready
            </div>

            <h3>AQI Prediction Model</h3>

            <p>
              A machine learning powered system designed to
              process air-quality features and generate AQI
              predictions.
            </p>
          </div>
        </div>

        <div className="model-hero-side">
          <span>MODEL STATUS</span>

          <strong>Ready</strong>

          <small>
            Backend integration pending
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
            <span>Input Features</span>
            <strong>6</strong>
            <small>Pollutant parameters</small>
          </div>
        </div>

        <div className="model-info-card">
          <div className="model-info-icon">
            <Layers3 size={21} />
          </div>

          <div>
            <span>Prediction Type</span>
            <strong>AQI</strong>
            <small>Air quality prediction</small>
          </div>
        </div>

        <div className="model-info-card">
          <div className="model-info-icon">
            <Server size={21} />
          </div>

          <div>
            <span>API Status</span>
            <strong>Pending</strong>
            <small>Waiting for backend</small>
          </div>
        </div>

        <div className="model-info-card">
          <div className="model-info-icon">
            <CheckCircle2 size={21} />
          </div>

          <div>
            <span>Frontend</span>
            <strong>Ready</strong>
            <small>Prediction UI connected</small>
          </div>
        </div>

      </section>


      {/* INPUT FEATURES */}
      <section className="model-section">

        <div className="model-section-heading">
          <div>
            <p className="label">MODEL INPUTS</p>

            <h3>Prediction Features</h3>

            <p>
              The prediction interface is prepared to accept
              the following air-quality parameters.
            </p>
          </div>

          <div className="feature-count">
            6 Features
          </div>
        </div>

        <div className="feature-grid">

          {features.map((feature) => (
            <div
              className="feature-card"
              key={feature.name}
            >
              <div className="feature-icon">
                <Activity size={17} />
              </div>

              <div>
                <strong>{feature.name}</strong>

                <span>{feature.description}</span>
              </div>

              <CheckCircle2
                size={17}
                className="feature-check"
              />
            </div>
          ))}

        </div>

      </section>


      {/* PIPELINE */}
      <section className="model-section">

        <div className="model-section-heading">
          <div>
            <p className="label">PREDICTION WORKFLOW</p>

            <h3>How the system works</h3>

            <p>
              The frontend prepares the user input and is
              designed to send it to the ML backend.
            </p>
          </div>
        </div>

        <div className="pipeline">

          {pipeline.map((step, index) => (
            <div
              className="pipeline-step"
              key={step.number}
            >
              <div className="pipeline-number">
                {step.number}
              </div>

              <div className="pipeline-content">
                <h4>{step.title}</h4>

                <p>{step.text}</p>
              </div>

              {index < pipeline.length - 1 && (
                <ArrowRight
                  className="pipeline-arrow"
                  size={19}
                />
              )}
            </div>
          ))}

        </div>

      </section>


      {/* MODEL METRICS */}
      <section className="model-section">

        <div className="model-section-heading">
          <div>
            <p className="label">MODEL EVALUATION</p>

            <h3>Performance Metrics</h3>

            <p>
              Actual evaluation values will be displayed here
              once they are provided by the ML/backend team.
            </p>
          </div>
        </div>

        <div className="metrics-grid">

          <div className="metric-card">
            <span>Accuracy / Score</span>
            <strong>—</strong>
            <small>Backend value pending</small>
          </div>

          <div className="metric-card">
            <span>MAE</span>
            <strong>—</strong>
            <small>Backend value pending</small>
          </div>

          <div className="metric-card">
            <span>RMSE</span>
            <strong>—</strong>
            <small>Backend value pending</small>
          </div>

          <div className="metric-card">
            <span>Model Version</span>
            <strong>—</strong>
            <small>To be connected</small>
          </div>

        </div>

      </section>


      {/* INTEGRATION */}
      <section className="integration-card">

        <div className="integration-icon">
          <Server size={23} />
        </div>

        <div className="integration-content">
          <p className="label">BACKEND INTEGRATION</p>

          <h3>Frontend is ready for API connection</h3>

          <p>
            The prediction form and result interface are already
            prepared. Once the backend endpoint and request
            format are finalized, the frontend can send the
            pollutant values and display the actual ML prediction.
          </p>
        </div>

        <div className="integration-status">
          <span></span>
          Waiting for API
        </div>

      </section>

    </div>
  );
}

export default App;