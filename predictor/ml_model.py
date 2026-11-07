import joblib
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "random_forest_model.pkl"
)

# Load trained model
model = joblib.load(MODEL_PATH)


def predict_demand(data):

    columns = [
        "Global_reactive_power",
        "Voltage",
        "Global_intensity",
        "Sub_metering_1",
        "Sub_metering_2",
        "Sub_metering_3",
        "Hour",
        "Day",
        "Month",
        "Year"
    ]

    df = pd.DataFrame([data], columns=columns)

    prediction = model.predict(df)

    return round(float(prediction[0]), 3)