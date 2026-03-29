"""Lag features and 24h-ahead PM2.5 target."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def build_features(df: pd.DataFrame, root: Path) -> pd.DataFrame:
    df = df.sort_values(["City", "Start"]).copy()
    df["hour"] = df["Start"].dt.hour
    df["dayofweek"] = df["Start"].dt.dayofweek
    df["month"] = df["Start"].dt.month
    df["is_weekend"] = df["dayofweek"].isin([5, 6]).astype(int)

    df["PM25_lag1"] = df.groupby("City")["PM2.5"].shift(1)
    df["PM25_lag24"] = df.groupby("City")["PM2.5"].shift(24)
    df["PM25_roll24"] = (
        df.groupby("City")["PM2.5"].rolling(24, min_periods=1).mean().reset_index(level=0, drop=True)
    )
    df["target_PM25_24h"] = df.groupby("City")["PM2.5"].shift(-24)
    df = df.dropna()

    out = root / "data/processed/features.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out)
    return df
