# app/ml/forecast_service.py

import joblib
import pandas as pd
from app.ml.preprocessing import preprocess_dataset

MODEL_PATH = "app/ml/best_model.pkl"


class ForecastService:

    def __init__(self):
        self.model = joblib.load(MODEL_PATH)

    def predict(self, df: pd.DataFrame):

        df = preprocess_dataset(df)

        features = [
            "hour",
            "day_of_week",
            "month",
            "is_weekend",
            "doctor_count",
            "avg_patient_age",
            "emergency_count",
        ]

        prediction = self.model.predict(df[features])

        return prediction.tolist()