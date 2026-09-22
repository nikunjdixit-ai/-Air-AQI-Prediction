import os
import joblib
import pandas as pd
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from .models import PredictionHistory
from .schemas import PredictRequest, PredictResponse, HistoryItemResponse
from . import crud
Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="AQI Prediction API",
    description="Backend service for AQI prediction using Machine Learning & SQLite",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "model")
CANDIDATE_MODELS = [
    os.path.join(MODEL_DIR, "best_model.pkl"),
    os.path.join(MODEL_DIR, "aqi_model.pkl"),
    os.path.join(MODEL_DIR, "random_forest_model.pkl"),
    os.path.join(MODEL_DIR, "linear_regression_model.pkl")
]
FEATURE_ORDER = [
    "PM2.5", "PM10", "NO", "NO2", "NOx", "NH3",
    "CO", "SO2", "O3", "Benzene", "Toluene", "Xylene",
    "Year", "Month", "Day"
]
POLLUTANT_DEFAULTS = {
    "PM2.5": 65.0, "PM10": 110.0, "NO": 15.0, "NO2": 25.0,
    "NOx": 30.0, "NH3": 20.0, "CO": 1.1, "SO2": 12.0,
    "O3": 35.0, "Benzene": 2.5, "Toluene": 6.0, "Xylene": 2.0
}
_model = None
_model_name = "None"

def load_ml_model():
    """Loads the first available trained ML model from the candidate list."""
    global _model, _model_name
    if _model is not None:
        return _model
    for path in CANDIDATE_MODELS:
        if os.path.exists(path):
            try:
                _model = joblib.load(path)
                _model_name = os.path.basename(path)
                return _model
            except Exception:
                continue
    return None
def calculate_cpcb_category(aqi: float) -> tuple[str, str]:
    """CPCB India AQI Category and Advisory."""
    if aqi <= 50:
        return "Good", "Air quality is good. Enjoy normal outdoor activities."
    elif aqi <= 100:
        return "Satisfactory", "Air quality is satisfactory. Sensitive individuals should be cautious."
    elif aqi <= 200:
        return "Moderate", "Minor breathing discomfort to sensitive people."
    elif aqi <= 300:
        return "Poor", "Breathing discomfort to most people on prolonged exposure."
    elif aqi <= 400:
        return "Very Poor", "Respiratory illness on prolonged exposure. Avoid strenuous outdoor activities."
    else:
        return "Severe", "Emergency health warning. Air quality is hazardous. Remain strictly indoors."
@app.get("/")
def root():
    return {"message": "Welcome to AQI Prediction Backend API", "docs": "/docs"}
@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.utcnow()}
@app.get("/model-info")
def model_info():
    model = load_ml_model()
    return {
        "model_file": _model_name,
        "features_expected": FEATURE_ORDER,
        "status": "loaded" if model is not None else "using fallback"
    }
@app.post("/predict", response_model=PredictResponse)
def predict_aqi(req: PredictRequest, db: Session = Depends(get_db)):
    model = load_ml_model()
    now = datetime.now()
    row = {
        "PM2.5": req.pm25,
        "PM10": req.pm10,
        "NO": POLLUTANT_DEFAULTS["NO"],
        "NO2": req.no2,
        "NOx": POLLUTANT_DEFAULTS["NOx"],
        "NH3": POLLUTANT_DEFAULTS["NH3"],
        "CO": req.co,
        "SO2": req.so2,
        "O3": req.o3,
        "Benzene": POLLUTANT_DEFAULTS["Benzene"],
        "Toluene": POLLUTANT_DEFAULTS["Toluene"],
        "Xylene": POLLUTANT_DEFAULTS["Xylene"],
        "Year": now.year,
        "Month": now.month,
        "Day": now.day
    }
    input_df = pd.DataFrame([row])[FEATURE_ORDER]
    if model is not None:
        raw_prediction = float(model.predict(input_df)[0])
    else:
        raw_prediction = (req.pm25 * 0.4) + (req.pm10 * 0.25) + (req.no2 * 0.15) + (req.co * 10) + (req.so2 * 0.1) + (req.o3 * 0.1) 
    predicted_aqi = round(max(0.0, raw_prediction), 2)
    category, advisory = calculate_cpcb_category(predicted_aqi)
    db_record = crud.save_prediction(db, req, predicted_aqi, category)
    return PredictResponse(
        id=db_record.id,
        predicted_aqi=predicted_aqi,
        category=category,
        advisory=advisory,
        timestamp=db_record.timestamp
    )
@app.get("/history", response_model=List[HistoryItemResponse])
def read_history(limit: int = 50, db: Session = Depends(get_db)):
    return crud.get_recent_history(db, limit=limit)