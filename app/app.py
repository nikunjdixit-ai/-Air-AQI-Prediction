import streamlit as st
import joblib
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "best_model.pkl"

model = joblib.load(MODEL_PATH)

st.set_page_config(page_title="AQI Prediction", page_icon="🌍")

st.title("🌍 Air Quality Index Prediction")
st.write("Predict AQI using Machine Learning")

def get_aqi_category(aqi):
    if aqi <= 50:
        return "🟢 Good"
    elif aqi <= 100:
        return "🟡 Satisfactory"
    elif aqi <= 200:
        return "🟠 Moderate"
    elif aqi <= 300:
        return "🔴 Poor"
    elif aqi <= 400:
        return "🟣 Very Poor"
    else:
        return "⚫ Severe"

st.header("Enter Pollution Levels")

pm25 = st.number_input("PM2.5", min_value=0.0)
pm10 = st.number_input("PM10", min_value=0.0)
no = st.number_input("NO", min_value=0.0)
no2 = st.number_input("NO2", min_value=0.0)
nox = st.number_input("NOx", min_value=0.0)
nh3 = st.number_input("NH3", min_value=0.0)
co = st.number_input("CO", min_value=0.0)
so2 = st.number_input("SO2", min_value=0.0)
o3 = st.number_input("O3", min_value=0.0)
benzene = st.number_input("Benzene", min_value=0.0)
toluene = st.number_input("Toluene", min_value=0.0)
xylene = st.number_input("Xylene", min_value=0.0)

year = st.number_input("Year", min_value=2000, max_value=2100, value=2026)
month = st.number_input("Month", min_value=1, max_value=12, value=7)
day = st.number_input("Day", min_value=1, max_value=31, value=18)

if st.button("Predict AQI"):

    input_data = np.array([[
        pm25,
        pm10,
        no,
        no2,
        nox,
        nh3,
        co,
        so2,
        o3,
        benzene,
        toluene,
        xylene,
        year,
        month,
        day
    ]])

    prediction = model.predict(input_data)
    predicted_aqi = prediction[0]

    st.success(f"Predicted AQI: {predicted_aqi:.2f}")

    category = get_aqi_category(predicted_aqi)

    st.info(f"AQI Category: {category}")