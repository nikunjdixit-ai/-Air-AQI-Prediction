"""
Flask Application for Air Quality Intelligence & AQI Prediction.
Provides a RESTful API and Web Interface for deployment on Render.
Main WSGI entrypoint: app:app
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict

# Ensure project root is at the head of sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, jsonify, request, render_template_string
from dotenv import load_dotenv

load_dotenv()

from src.predictor import predict_aqi_rich, load_model
from src.tools.live_aqi_tool import fetch_live_air_quality
from src.tools.prediction_tool import predict_aqi_tool
from src.agent.orchestrator import AirQualityAgent

# Initialize Flask application instance
app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

# Lazy-load agent instance
_agent_instance = None


def get_agent() -> AirQualityAgent:
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = AirQualityAgent()
    return _agent_instance


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Air Quality Intelligence Service</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        .hero { background: linear-gradient(135deg, #1e3a8a 0%, #0284c7 100%); color: white; padding: 3rem 1rem; border-radius: 0 0 20px 20px; }
        .card { border: none; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 1.5rem; }
        .endpoint-badge { font-family: monospace; font-size: 0.85rem; }
    </style>
</head>
<body>
    <div class="hero text-center mb-4">
        <h1 class="fw-bold">🌍 Air Quality Intelligence Service</h1>
        <p class="lead mb-0">Production Flask API & ML Prediction Engine for Render</p>
    </div>
    <div class="container mb-5">
        <div class="row">
            <div class="col-md-6">
                <div class="card p-4">
                    <h4 class="fw-bold mb-3">🔍 Quick AQI Prediction</h4>
                    <form id="predictForm">
                        <div class="mb-3">
                            <label class="form-label">City / Location</label>
                            <input type="text" class="form-control" id="cityInput" value="Delhi" required>
                        </div>
                        <div class="row">
                            <div class="col-6 mb-3">
                                <label class="form-label">PM2.5 (µg/m³)</label>
                                <input type="number" step="0.1" class="form-control" id="pm25Input" value="55.0">
                            </div>
                            <div class="col-6 mb-3">
                                <label class="form-label">PM10 (µg/m³)</label>
                                <input type="number" step="0.1" class="form-control" id="pm10Input" value="95.0">
                            </div>
                        </div>
                        <button type="submit" class="btn btn-primary w-100">Predict AQI</button>
                    </form>
                    <div id="predictResult" class="mt-3 p-3 bg-light rounded d-none"></div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card p-4">
                    <h4 class="fw-bold mb-3">🤖 Ask the AI Agent</h4>
                    <form id="agentForm">
                        <div class="mb-3">
                            <label class="form-label">Natural Language Question</label>
                            <input type="text" class="form-control" id="agentQuery" value="Should I go for a morning run in Delhi tomorrow?" required>
                        </div>
                        <button type="submit" class="btn btn-success w-100">Consult Agent</button>
                    </form>
                    <div id="agentResult" class="mt-3 p-3 bg-light rounded d-none"></div>
                </div>
            </div>
        </div>

        <div class="card p-4">
            <h4 class="fw-bold mb-3">📚 Available API Endpoints</h4>
            <div class="list-group">
                <div class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        <span class="badge bg-success endpoint-badge">GET</span> <code>/health</code>
                        <div class="text-muted small">Service health status check for Render uptime monitoring</div>
                    </div>
                    <a href="/health" class="btn btn-sm btn-outline-primary" target="_blank">Test</a>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        <span class="badge bg-primary endpoint-badge">POST</span> <code>/predict</code>
                        <div class="text-muted small">Predict AQI using the trained Random Forest model (Accepts JSON payload or query params)</div>
                    </div>
                    <span class="text-muted small">JSON / Form</span>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        <span class="badge bg-primary endpoint-badge">POST</span> <code>/agent</code>
                        <div class="text-muted small">Ask questions to the multi-tool autonomous Air Quality Intelligence Agent</div>
                    </div>
                    <span class="text-muted small">JSON: {"query": "..."}</span>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        <span class="badge bg-info text-dark endpoint-badge">GET</span> <code>/live?city=Delhi</code>
                        <div class="text-muted small">Fetch live air quality readings and driver pollutant from monitoring stations</div>
                    </div>
                    <a href="/live?city=Delhi" class="btn btn-sm btn-outline-primary" target="_blank">Test</a>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('predictForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const resultBox = document.getElementById('predictResult');
            resultBox.classList.remove('d-none');
            resultBox.innerHTML = '<em>Calculating ML forecast...</em>';
            try {
                const res = await fetch('/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        location: document.getElementById('cityInput').value,
                        PM25: parseFloat(document.getElementById('pm25Input').value) || 0,
                        PM10: parseFloat(document.getElementById('pm10Input').value) || 0
                    })
                });
                const data = await res.json();
                resultBox.innerHTML = `<strong>Predicted AQI:</strong> ${data.aqi} (${data.category})<br>
                                       <strong>Dominant Factor:</strong> ${data.dominant_pollutant || 'N/A'}<br>
                                       <small class="text-muted">${data.health_message || ''}</small>`;
            } catch (err) {
                resultBox.innerHTML = `<span class="text-danger">Error: ${err.message}</span>`;
            }
        });

        document.getElementById('agentForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const resultBox = document.getElementById('agentResult');
            resultBox.classList.remove('d-none');
            resultBox.innerHTML = '<em>Agent reasoning and calling tools...</em>';
            try {
                const res = await fetch('/agent', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: document.getElementById('agentQuery').value })
                });
                const data = await res.json();
                resultBox.innerHTML = `<div style="white-space: pre-wrap;">${data.response}</div>`;
            } catch (err) {
                resultBox.innerHTML = `<span class="text-danger">Error: ${err.message}</span>`;
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
    return jsonify({
        "status": "healthy",
        "service": "Flask Air Quality Intelligence Service",
        "version": "1.0.0",
        "framework": "Flask 3.1",
        "model_loaded": load_model() is not None
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
    Accepts JSON body or query parameters.
    """
    payload: Dict[str, Any] = {}

    if request.method == "POST":
        if request.is_json:
            payload = request.get_json(silent=True) or {}
        else:
            payload = request.form.to_dict()
    else:
        payload = request.args.to_dict()

    location = payload.get("location") or payload.get("city")
    target_date = payload.get("target_date") or payload.get("date")

    # Clean pollutant keys
    pollutant_data = {}
    for k, v in payload.items():
        clean_k = k.replace(".", "").upper()
        if clean_k in ["PM25", "PM2_5"]:
            pollutant_data["PM2.5"] = float(v)
        elif clean_k in ["PM10", "NO", "NO2", "NOX", "NH3", "CO", "SO2", "O3", "BENZENE", "TOLUENE", "XYLENE"]:
            orig_key = "PM10" if clean_k == "PM10" else "NO2" if clean_k == "NO2" else "SO2" if clean_k == "SO2" else "CO" if clean_k == "CO" else "O3" if clean_k == "O3" else clean_k.capitalize()
            try:
                pollutant_data[orig_key] = float(v)
            except (ValueError, TypeError):
                pass

    try:
        result = predict_aqi_tool(
            input_data=pollutant_data if pollutant_data else None,
            location=location,
            target_date=target_date
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Prediction failed: {str(e)}"
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

    if not query:
        return jsonify({
            "status": "error",
            "message": "Missing 'query' parameter."
        }), 400

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
        return jsonify({
            "status": "error",
            "message": f"Agent query failed: {str(e)}"
        }), 500


if __name__ == "__main__":
    # Render binds the port via the PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
