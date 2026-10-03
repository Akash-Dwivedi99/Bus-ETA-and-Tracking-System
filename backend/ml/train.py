"""
Trains a baseline ETA prediction model from historical trip data
(synopsis §5.8-5.9 — the "future stage" ML-based ETA).

This is deliberately simple (linear regression, a handful of features)
since it needs real trip volume to be worth more than that. Swap in a
better model once data/trips.csv has real logged trips instead of the
synthetic sample rows.

Run:
  pip install pandas scikit-learn joblib
  python ml/train.py
"""

import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "trips.csv")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "eta_model.joblib")

FEATURES = ["distance_km", "avg_speed_kmph", "hour_of_day", "day_of_week"]
TARGET = "actual_travel_time_min"


def main():
    df = pd.read_csv(DATA_PATH)

    if len(df) < 10:
        print(f"Only {len(df)} rows in {DATA_PATH} — predictions will be unreliable "
              "until there's real logged trip data. Training anyway for demo purposes.")

    X = df[FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression().fit(X_train, y_train)

    preds = model.predict(X_test)
    print("MAE:", round(mean_absolute_error(y_test, preds), 2))
    print("RMSE:", round(mean_squared_error(y_test, preds) ** 0.5, 2))
    print("R2:", round(r2_score(y_test, preds), 3))

    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    main()
