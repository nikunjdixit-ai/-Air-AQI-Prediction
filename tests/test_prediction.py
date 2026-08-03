import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.predictor import predict_aqi
from src.aqi_utils import get_aqi_status


sample_data = {
    "PM2.5": 80,
    "PM10": 120,
    "NO": 40,
    "NO2": 30,
    "NOx": 50,
    "NH3": 20,
    "CO": 1.0,
    "SO2": 20,
    "O3": 50,
    "Benzene": 2,
    "Toluene": 5,
    "Xylene": 1,
    "Year": 2026,
    "Month": 8,
    "Day": 2
}


prediction = predict_aqi(sample_data)

result = get_aqi_status(prediction)


print("AQI Prediction System")
print("---------------------")

print(f"Predicted AQI : {result['aqi']}")
print(f"Category      : {result['category']}")
print(f"Health Advice : {result['message']}")