"""
Flask Application for Air Quality Intelligence & AQI Prediction.
Provides a RESTful API and Web Interface for deployment on Render.
Main WSGI entrypoint: app:app
"""

from datetime import datetime
import logging
import os
from pathlib import Path
import re
import sys
from typing import Any, Dict, Optional, Tuple

# Ensure project root is at the head of sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, jsonify, render_template_string, request
from dotenv import load_dotenv

load_dotenv()

from src.predictor import predict_aqi_rich, load_model
from src.tools.live_aqi_tool import fetch_live_air_quality
from src.tools.prediction_tool import predict_aqi_tool
from src.agent.orchestrator import AirQualityAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("flask_app")

# Initialize Flask application instance
app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

# Lazy-loaded agent instance
_agent_instance = None


def get_agent() -> AirQualityAgent:
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = AirQualityAgent()
    return _agent_instance


# Supported pollutant alias mappings to canonical model feature names
POLLUTANT_ALIAS_MAP = {
    "PM2.5": ["PM25", "PM2_5", "PM2.5"],
    "PM10": ["PM10"],
    "NO": ["NO"],
    "NO2": ["NO2"],
    "NOx": ["NOX"],
    "NH3": ["NH3"],
    "CO": ["CO"],
    "SO2": ["SO2"],
    "O3": ["O3"],
    "Benzene": ["BENZENE"],
    "Toluene": ["TOLUENE"],
    "Xylene": ["XYLENE"]
}

# Inverted mapping for quick canonical feature lookup
CANONICAL_LOOKUP = {}
for canonical, aliases in POLLUTANT_ALIAS_MAP.items():
    for alias in aliases:
        CANONICAL_LOOKUP[alias] = canonical


def validate_and_extract_payload(raw_data: Dict[str, Any]) -> Tuple[Optional[Dict[str, float]], Optional[str], Optional[str], Optional[str]]:
    """
    Validate and extract pollutant values, location, and target date.
    Returns: (pollutant_data, location, target_date, error_message)
    """
    pollutant_data: Dict[str, float] = {}
    location = raw_data.get("location") or raw_data.get("city")
    if location:
        location = str(location).strip()
        if len(location) > 100:
            return None, None, None, "Location name is too long (maximum 100 characters)."

    target_date = raw_data.get("target_date") or raw_data.get("date")
    if target_date:
        target_date = str(target_date).strip()
        if target_date.lower() not in ["today", "tomorrow"]:
            # Validate YYYY-MM-DD
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", target_date):
                return None, None, None, f"Invalid date '{target_date}'. Expected 'YYYY-MM-DD', 'today', or 'tomorrow'."
            try:
                datetime.strptime(target_date, "%Y-%m-%d")
            except ValueError:
                return None, None, None, f"Invalid calendar date '{target_date}'."

    for raw_k, raw_v in raw_data.items():
        if raw_v is None:
            continue
        str_v = str(raw_v).strip()
        if str_v == "":
            continue

        clean_k = raw_k.replace(".", "").replace("_", "").upper()
        # Find matching canonical feature
        matched_feature = None
        for alias, canonical in CANONICAL_LOOKUP.items():
            if clean_k == alias.replace(".", "").replace("_", "").upper():
                matched_feature = canonical
                break

        if matched_feature:
            try:
                numeric_val = float(str_v)
            except (ValueError, TypeError):
                return None, None, None, f"Invalid input for '{matched_feature}': expected a numeric value, but received '{raw_v}'."

            if numeric_val < 0.0:
                return None, None, None, f"Invalid input for '{matched_feature}': concentration cannot be negative ({numeric_val})."

            pollutant_data[matched_feature] = numeric_val

    return pollutant_data, location, target_date, None


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Air Quality Intelligence & Prediction Service</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <style>
        body { background-color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; color: #1e293b; }
        .hero { background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #0284c7 100%); color: white; padding: 3.5rem 1rem; border-radius: 0 0 24px 24px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.2); }
        .card { border: none; border-radius: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -2px rgba(0,0,0,0.05); }
        .card-header-custom { background: transparent; border-bottom: 1px solid #e2e8f0; font-weight: 700; }
        .endpoint-badge { font-family: monospace; font-weight: 700; font-size: 0.8rem; }
        .aqi-score-box { border-radius: 16px; padding: 1.5rem; text-align: center; color: white; margin-bottom: 1rem; }
        .aqi-value { font-size: 3.5rem; font-weight: 800; line-height: 1; }
        .aqi-cat { font-size: 1.25rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
        .factor-bar { height: 8px; border-radius: 4px; background: #e2e8f0; overflow: hidden; margin-top: 4px; }
        .factor-fill { height: 100%; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="hero text-center mb-4">
        <div class="container">
            <span class="badge bg-primary-subtle text-primary-emphasis border border-primary-subtle px-3 py-2 rounded-pill mb-3">
                <i class="bi bi-shield-check me-1"></i> Production Ready &amp; Render Deployed
            </span>
            <h1 class="display-5 fw-bold mb-2">🌍 Air Quality Intelligence Service</h1>
            <p class="lead mb-0 text-slate-200">Autonomous AI Agent &amp; Machine Learning AQI Forecast API</p>
        </div>
    </div>

    <div class="container mb-5">
        <!-- Live System Status Bar -->
        <div class="card p-3 mb-4 bg-white">
            <div class="d-flex flex-wrap justify-content-between align-items-center gap-2">
                <div class="d-flex align-items-center gap-2">
                    <span class="spinner-grow spinner-grow-sm text-success" role="status"></span>
                    <span class="fw-semibold">System Status:</span>
                    <span class="badge bg-success-subtle text-success border border-success-subtle">Online &amp; Healthy</span>
                </div>
                <div class="d-flex gap-3 text-muted small">
                    <span><i class="bi bi-cpu me-1"></i> Model: <strong>Random Forest (15 Features)</strong></span>
                    <span><i class="bi bi-hdd-network me-1"></i> WSGI: <strong>Gunicorn / Render</strong></span>
                </div>
            </div>
        </div>

        <div class="row g-4">
            <!-- Left Column: Prediction Form -->
            <div class="col-lg-6">
                <div class="card h-100 p-4 bg-white">
                    <div class="card-header-custom pb-3 mb-3">
                        <h4 class="mb-1"><i class="bi bi-calculator text-primary me-2"></i>Predict AQI Index</h4>
                        <small class="text-muted">Enter monitored pollutants or city name for machine learning forecast</small>
                    </div>

                    <form id="predictForm" method="POST" action="/predict">
                        <div class="mb-3">
                            <label class="form-label fw-semibold">Location / City Context</label>
                            <div class="input-group">
                                <span class="input-group-text"><i class="bi bi-geo-alt"></i></span>
                                <input type="text" class="form-control" name="location" id="cityInput" value="Delhi" placeholder="e.g., Delhi, Kanpur, Mumbai" required>
                            </div>
                        </div>

                        <div class="row g-3 mb-3">
                            <div class="col-6">
                                <label class="form-label fw-semibold">PM2.5 (µg/m³)</label>
                                <input type="number" step="any" min="0" class="form-control" name="PM2.5" id="pm25Input" value="55.0" placeholder="e.g., 55.0">
                                <div class="form-text">Fine inhalable particles (Safe: 60)</div>
                            </div>
                            <div class="col-6">
                                <label class="form-label fw-semibold">PM10 (µg/m³)</label>
                                <input type="number" step="any" min="0" class="form-control" name="PM10" id="pm10Input" value="95.0" placeholder="e.g., 95.0">
                                <div class="form-text">Coarse dust particles (Safe: 100)</div>
                            </div>
                        </div>

                        <!-- Collapsible for other pollutants -->
                        <div class="accordion mb-3" id="pollutantAccordion">
                            <div class="accordion-item border rounded-3">
                                <h2 class="accordion-header">
                                    <button class="accordion-button collapsed py-2 text-muted" type="button" data-bs-toggle="collapse" data-bs-target="#collapsePollutants">
                                        <i class="bi bi-sliders me-2"></i> Additional Pollutants (Optional)
                                    </button>
                                </h2>
                                <div id="collapsePollutants" class="accordion-collapse collapse">
                                    <div class="accordion-body">
                                        <div class="row g-2">
                                            <div class="col-6">
                                                <label class="form-label small mb-1">NO2 (µg/m³)</label>
                                                <input type="number" step="any" min="0" class="form-control form-control-sm" name="NO2" id="no2Input" placeholder="Default: 25.0">
                                            </div>
                                            <div class="col-6">
                                                <label class="form-label small mb-1">SO2 (µg/m³)</label>
                                                <input type="number" step="any" min="0" class="form-control form-control-sm" name="SO2" id="so2Input" placeholder="Default: 12.0">
                                            </div>
                                            <div class="col-6">
                                                <label class="form-label small mb-1">CO (mg/m³)</label>
                                                <input type="number" step="any" min="0" class="form-control form-control-sm" name="CO" id="coInput" placeholder="Default: 1.1">
                                            </div>
                                            <div class="col-6">
                                                <label class="form-label small mb-1">O3 (µg/m³)</label>
                                                <input type="number" step="any" min="0" class="form-control form-control-sm" name="O3" id="o3Input" placeholder="Default: 35.0">
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="d-grid">
                            <button type="submit" id="predictBtn" class="btn btn-primary btn-lg shadow-sm">
                                <i class="bi bi-lightning-charge-fill me-1"></i> Calculate Forecast
                            </button>
                        </div>
                    </form>

                    <!-- Prediction Result Container -->
                    <div id="predictResult" class="mt-4 d-none"></div>
                </div>
            </div>

            <!-- Right Column: AI Agent Consultation -->
            <div class="col-lg-6">
                <div class="card h-100 p-4 bg-white">
                    <div class="card-header-custom pb-3 mb-3">
                        <h4 class="mb-1"><i class="bi bi-robot text-success me-2"></i>Consult AI Agent</h4>
                        <small class="text-muted">Ask questions in natural language with multi-tool reasoning</small>
                    </div>

                    <form id="agentForm" method="POST" action="/agent">
                        <div class="mb-3">
                            <label class="form-label fw-semibold">Your Question</label>
                            <textarea class="form-control" name="query" id="agentQuery" rows="3" placeholder="e.g., I want to go for a morning run in Delhi tomorrow. Is it safe?" required>I want to go for a morning run in Delhi tomorrow. Is it safe?</textarea>
                        </div>
                        <div class="d-flex flex-wrap gap-1 mb-3">
                            <span class="badge bg-light text-secondary border cursor-pointer quick-query" style="cursor: pointer;">AQI in Kanpur right now?</span>
                            <span class="badge bg-light text-secondary border cursor-pointer quick-query" style="cursor: pointer;">Why is air quality poor today?</span>
                            <span class="badge bg-light text-secondary border cursor-pointer quick-query" style="cursor: pointer;">What is the dominant pollutant?</span>
                        </div>
                        <div class="d-grid">
                            <button type="submit" id="agentBtn" class="btn btn-success btn-lg shadow-sm">
                                <i class="bi bi-chat-dots-fill me-1"></i> Consult Agent
                            </button>
                        </div>
                    </form>

                    <!-- Agent Result Container -->
                    <div id="agentResult" class="mt-4 d-none"></div>
                </div>
            </div>
        </div>

        <!-- API Reference Cards -->
        <div class="card mt-4 p-4 bg-white">
            <h4 class="fw-bold mb-3"><i class="bi bi-code-slash text-secondary me-2"></i>REST API Endpoints for Integration</h4>
            <div class="list-group list-group-flush">
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                    <div>
                        <span class="badge bg-success endpoint-badge me-2">GET</span> <code>/health</code>
                        <div class="text-muted small mt-1">Uptime check verifying model deserialization and memory integrity.</div>
                    </div>
                    <a href="/health" class="btn btn-sm btn-outline-primary" target="_blank">Test JSON</a>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                    <div>
                        <span class="badge bg-primary endpoint-badge me-2">POST</span> <code>/predict</code>
                        <div class="text-muted small mt-1">Pass JSON or Form parameters (e.g., <code>{"location": "Delhi", "PM2.5": 55.0}</code>).</div>
                    </div>
                    <span class="badge bg-light text-dark border">JSON / Form</span>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                    <div>
                        <span class="badge bg-primary endpoint-badge me-2">POST</span> <code>/agent</code>
                        <div class="text-muted small mt-1">Submit natural language queries to the autonomous multi-tool agent.</div>
                    </div>
                    <span class="badge bg-light text-dark border">JSON: {"query": "..."}</span>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                    <div>
                        <span class="badge bg-info text-dark endpoint-badge me-2">GET</span> <code>/live?city=Delhi</code>
                        <div class="text-muted small mt-1">Fetch live monitoring station pollutants and real-time AQI.</div>
                    </div>
                    <a href="/live?city=Delhi" class="btn btn-sm btn-outline-primary" target="_blank">Test JSON</a>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Quick query chip clicks
        document.querySelectorAll('.quick-query').forEach(chip => {
            chip.addEventListener('click', () => {
                document.getElementById('agentQuery').value = chip.textContent.trim();
            });
        });

        // Category Colors
        function getCategoryColor(cat) {
            const c = (cat || '').toLowerCase();
            if (c.includes('good')) return '#10B981';
            if (c.includes('satisfactory')) return '#FBBF24';
            if (c.includes('moderate')) return '#F97316';
            if (c.includes('poor') && !c.includes('very')) return '#EF4444';
            if (c.includes('very poor')) return '#8B5CF6';
            return '#881337';
        }

        // Predict Form Submit via AJAX
        document.getElementById('predictForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('predictBtn');
            const resultBox = document.getElementById('predictResult');
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Forecasting...';

            resultBox.classList.remove('d-none');
            resultBox.innerHTML = '<div class="text-center py-3 text-muted"><div class="spinner-border text-primary spinner-border-sm me-2"></div>Evaluating tabular features and neural factors...</div>';

            const payload = {
                location: document.getElementById('cityInput').value,
                "PM2.5": document.getElementById('pm25Input').value,
                "PM10": document.getElementById('pm10Input').value
            };

            const no2 = document.getElementById('no2Input').value;
            const so2 = document.getElementById('so2Input').value;
            const co = document.getElementById('coInput').value;
            const o3 = document.getElementById('o3Input').value;

            if (no2) payload["NO2"] = no2;
            if (so2) payload["SO2"] = so2;
            if (co) payload["CO"] = co;
            if (o3) payload["O3"] = o3;

            try {
                const res = await fetch('/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();

                if (!res.ok || data.status === 'error') {
                    resultBox.innerHTML = `
                        <div class="alert alert-danger d-flex align-items-center border-0 shadow-sm" role="alert">
                            <i class="bi bi-exclamation-triangle-fill fs-4 me-3"></i>
                            <div>
                                <div class="fw-bold">Prediction Error</div>
                                <div>${data.message || 'Validation or processing error occurred.'}</div>
                            </div>
                        </div>`;
                    return;
                }

                const catColor = data.color || getCategoryColor(data.category);
                let factorsHtml = '';
                if (data.major_factors && data.major_factors.length > 0) {
                    factorsHtml = '<div class="mt-3"><div class="fw-semibold small text-muted mb-2">KEY DRIVING POLLUTANTS</div>' +
                        data.major_factors.map(f => `
                            <div class="mb-2">
                                <div class="d-flex justify-content-between small">
                                    <span><strong>${f.pollutant}</strong> (${f.measured_value} µg/m³)</span>
                                    <span class="badge ${f.impact_level === 'Critical' ? 'bg-danger' : f.impact_level === 'High' ? 'bg-warning text-dark' : 'bg-light text-dark border'}">${f.impact_level}</span>
                                </div>
                                <div class="factor-bar"><div class="factor-fill" style="width: ${Math.min(100, (f.ratio_to_safe_limit || 0) * 100)}%; background-color: ${catColor};"></div></div>
                            </div>
                        `).join('') + '</div>';
                }

                resultBox.innerHTML = `
                    <div class="aqi-score-box shadow-sm" style="background-color: ${catColor};">
                        <div class="small opacity-75">PREDICTED AIR QUALITY INDEX</div>
                        <div class="aqi-value my-1">${data.aqi}</div>
                        <div class="aqi-cat">${data.category}</div>
                        <div class="mt-2 small opacity-90"><i class="bi bi-geo-alt me-1"></i>${data.location_context} &bull; Forecast for ${data.target_date || 'Today'}</div>
                    </div>
                    <div class="card p-3 border bg-light">
                        <div class="fw-bold text-dark mb-1"><i class="bi bi-heart-pulse text-danger me-2"></i>Health Guidance</div>
                        <div class="text-secondary small mb-2">${data.health_message || 'Maintain awareness of local pollution levels.'}</div>
                        ${factorsHtml}
                    </div>
                `;

            } catch (err) {
                resultBox.innerHTML = `
                    <div class="alert alert-danger border-0 shadow-sm">
                        <i class="bi bi-wifi-off me-2"></i><strong>Network Error:</strong> ${err.message}
                    </div>`;
            } finally {
                btn.disabled = false;
                btn.innerHTML = '<i class="bi bi-lightning-charge-fill me-1"></i> Calculate Forecast';
            }
        });

        // Agent Form Submit via AJAX
        document.getElementById('agentForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('agentBtn');
            const resultBox = document.getElementById('agentResult');
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Consulting Agent...';

            resultBox.classList.remove('d-none');
            resultBox.innerHTML = '<div class="text-center py-3 text-muted"><div class="spinner-border text-success spinner-border-sm me-2"></div>Agent orchestrating tools &amp; synthesizing report...</div>';

            try {
                const res = await fetch('/agent', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
                    body: JSON.stringify({ query: document.getElementById('agentQuery').value })
                });
                const data = await res.json();

                if (!res.ok || data.status === 'error') {
                    resultBox.innerHTML = `
                        <div class="alert alert-danger border-0 shadow-sm">
                            <i class="bi bi-exclamation-octagon-fill me-2"></i><strong>Agent Error:</strong> ${data.message || 'Agent failed to process query.'}
                        </div>`;
                    return;
                }

                let activityHtml = '';
                if (data.activity && data.activity.length > 0) {
                    activityHtml = '<div class="p-2 bg-light border rounded small mb-3">' +
                        '<div class="fw-bold text-secondary mb-1"><i class="bi bi-gear-wide-connected me-1"></i>Tool Execution Trace:</div>' +
                        '<ul class="mb-0 ps-3">' + data.activity.map(a => `<li>${a}</li>`).join('') + '</ul>' +
                        '</div>';
                }

                resultBox.innerHTML = `
                    ${activityHtml}
                    <div class="card p-3 border shadow-sm" style="white-space: pre-wrap; font-family: inherit;">
                        ${data.response}
                    </div>
                `;
            } catch (err) {
                resultBox.innerHTML = `
                    <div class="alert alert-danger border-0 shadow-sm">
                        <i class="bi bi-wifi-off me-2"></i><strong>Network Error:</strong> ${err.message}
                    </div>`;
            } finally {
                btn.disabled = false;
                btn.innerHTML = '<i class="bi bi-chat-dots-fill me-1"></i> Consult Agent';
            }
        });
    </script>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def index():
    """Web interface / documentation portal."""
    return render_template_string(HTML_TEMPLATE)


@app.route("/health", methods=["GET"])
@app.route("/status", methods=["GET"])
def health():
    """Health check endpoint for Render service uptime checks."""
    try:
        model = load_model()
        model_loaded = model is not None
    except Exception as e:
        logger.error("Health check model loading failed: %s", e)
        return jsonify({
            "status": "unhealthy",
            "error": f"Model failed to load: {str(e)}"
        }), 500

    return jsonify({
        "status": "healthy",
        "service": "Flask Air Quality Intelligence Service",
        "version": "1.1.0",
        "framework": "Flask 3.1",
        "model_loaded": model_loaded
    }), 200


@app.route("/live", methods=["GET"])
def live_aqi():
    """Retrieve real-time atmospheric sensor data for a city."""
    city = request.args.get("city") or request.args.get("location") or "Delhi"
    result = fetch_live_air_quality(city)
    status_code = 200 if result.get("status") == "success" else 400
    return jsonify(result), status_code


@app.route("/predict", methods=["GET", "POST"])
def predict():
    """
    Predict AQI using the trained Random Forest model.
    Validates input values strictly and returns descriptive 400 Bad Request
    on non-numeric or negative inputs, avoiding 500 server errors.
    """
    raw_payload: Dict[str, Any] = {}

    if request.method == "POST":
        if request.is_json:
            raw_payload = request.get_json(silent=True) or {}
        else:
            raw_payload = request.form.to_dict()
    else:
        raw_payload = request.args.to_dict()

    # Validate and extract features
    pollutant_data, location, target_date, validation_error = validate_and_extract_payload(raw_payload)

    if validation_error:
        logger.warning("Prediction rejected: %s", validation_error)
        return jsonify({
            "status": "error",
            "message": validation_error
        }), 400

    try:
        result = predict_aqi_tool(
            input_data=pollutant_data if pollutant_data else None,
            location=location,
            target_date=target_date
        )

        if result.get("status") == "error":
            return jsonify(result), 400

        return jsonify(result), 200

    except Exception as e:
        logger.exception("Prediction failed unexpectedly: %s", e)
        return jsonify({
            "status": "error",
            "message": f"Prediction computation failed: {str(e)}"
        }), 500


@app.route("/agent", methods=["GET", "POST"])
def agent_query():
    """
    Query the autonomous Air Quality Intelligence Agent.
    Accepts JSON: {"query": "..."} or GET query parameter: ?query=...
    """
    query = ""
    if request.method == "POST":
        if request.is_json:
            data = request.get_json(silent=True) or {}
            query = data.get("query", "")
        else:
            query = request.form.get("query", "")
    else:
        query = request.args.get("query", "")

    if not query or not str(query).strip():
        return jsonify({
            "status": "error",
            "message": "Missing required 'query' parameter."
        }), 400

    query = str(query).strip()

    try:
        agent = get_agent()
        res = agent.run(query)
        return jsonify({
            "status": "success",
            "query": query,
            "response": res["response"],
            "activity": res["activity"],
            "tool_outputs": res["tool_outputs"],
            "location": res["location"]
        }), 200
    except Exception as e:
        logger.exception("Agent execution failed: %s", e)
        return jsonify({
            "status": "error",
            "message": f"Agent query failed: {str(e)}"
        }), 500


if __name__ == "__main__":
    # Render binds the port via the PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
