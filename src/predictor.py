import joblib
import pandas as pd


MODEL_PATH = "models/best_model.pkl"


def load_model():
    """Load the trained AQI prediction model."""

    return joblib.load(MODEL_PATH)


def prepare_input(data):
    """Prepare input data in the format expected by the model."""

    feature_order = [
        "PM2.5",
        "PM10",
        "NO",
        "NO2",
        "NOx",
        "NH3",
        "CO",
        "SO2",
        "O3",
        "Benzene",
        "Toluene",
        "Xylene",
        "Year",
        "Month",
        "Day"
    ]

    input_df = pd.DataFrame([data])

    return input_df[feature_order]


def predict_aqi(data):
    """Predict AQI using the trained model."""

    model = load_model()

    input_df = prepare_input(data)

    prediction = model.predict(input_df)

    return prediction[0]