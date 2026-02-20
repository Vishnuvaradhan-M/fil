# app/ml/preprocessing.py

import pandas as pd


def preprocess_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df["day_of_week"] = df["appointment_date"].dt.weekday
    df["month"] = df["appointment_date"].dt.month
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)

    df = df.fillna(0)

    return df


def get_features_and_target(df: pd.DataFrame):
    features = [
        "hour",
        "day_of_week",
        "month",
        "is_weekend",
        "doctor_count",
        "avg_patient_age",
        "emergency_count",
    ]

    target = "appointment_count"

    return df[features], df[target]