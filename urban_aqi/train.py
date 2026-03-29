"""Train XGBoost regressor; persist pickle + metadata."""

from __future__ import annotations

import json
import pickle
from pathlib import Path

import pandas as pd
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
from xgboost import XGBRegressor


FEATURES = [
    "hour",
    "dayofweek",
    "month",
    "is_weekend",
    "PM25_lag1",
    "PM25_lag24",
    "PM25_roll24",
    "temperature_2m",
    "relative_humidity_2m",
    "wind_speed_10m",
]
TARGET = "target_PM25_24h"


def train_and_save(root: Path) -> dict:
    df = pd.read_parquet(root / "data/processed/features.parquet")
    train = df[df["Start"].dt.year == 2022]
    test = df[df["Start"].dt.year == 2025]
    if train.empty or test.empty:
        split_idx = int(len(df) * 0.8)
        train = df.iloc[:split_idx]
        test = df.iloc[split_idx:]

    X_train, y_train = train[FEATURES], train[TARGET]
    X_test, y_test = test[FEATURES], test[TARGET]

    model = XGBRegressor(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        random_state=42,
    )
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    mae = float(mean_absolute_error(y_test, preds))
    rmse = float(root_mean_squared_error(y_test, preds))

    models_dir = root / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    with (models_dir / "model.pkl").open("wb") as f:
        pickle.dump(model, f)

    meta = {"features": FEATURES, "mae": mae, "rmse": rmse}
    with (models_dir / "model_metadata.json").open("w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    return meta
