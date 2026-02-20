# app/ml/train_forecasting.py

import joblib
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from app.ml.dataset_builder import build_ml_dataset
from app.ml.preprocessing import preprocess_dataset, get_features_and_target
from app.ml.evaluation import evaluate_model

MODEL_PATH = "app/ml/best_model.pkl"


def train_models():

    df = build_ml_dataset()
    df = preprocess_dataset(df)

    X, y = get_features_and_target(df)

    train_size = int(len(df) * 0.7)
    val_size = int(len(df) * 0.15)

    X_train = X[:train_size]
    y_train = y[:train_size]

    X_val = X[train_size:train_size + val_size]
    y_val = y[train_size:train_size + val_size]

    X_test = X[train_size + val_size:]
    y_test = y[train_size + val_size:]

    models = {
        "LinearRegression": Pipeline([
            ("scaler", StandardScaler()),
            ("model", LinearRegression())
        ]),
        "RandomForest": RandomForestRegressor(n_estimators=300, random_state=42),
        "XGBoost": XGBRegressor(n_estimators=300, random_state=42),
    }

    best_model = None
    best_rmse = float("inf")

    for name, model in models.items():
        model.fit(X_train, y_train)
        val_pred = model.predict(X_val)

        metrics = evaluate_model(y_val, val_pred)
        print(f"\n{name} Validation Metrics:", metrics)

        if metrics["RMSE"] < best_rmse:
            best_rmse = metrics["RMSE"]
            best_model = model

    test_pred = best_model.predict(X_test)
    print("\nFinal Test Metrics:", evaluate_model(y_test, test_pred))

    joblib.dump(best_model, MODEL_PATH)
    print("Best model saved.")


if __name__ == "__main__":
    train_models()