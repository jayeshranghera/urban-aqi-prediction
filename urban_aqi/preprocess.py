"""Imputation, DuckDB export, aqi_clean.parquet."""

from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd


def preprocess_merged(df: pd.DataFrame, root: Path) -> pd.DataFrame:
    processed = root / "data/processed"
    processed.mkdir(parents=True, exist_ok=True)

    df = df.copy()
    df["Start"] = pd.to_datetime(df["Start"])
    df = df.sort_values(["City", "Start"])

    pollutants = ["PM2.5", "PM10", "NO2", "O3"]
    for p in pollutants:
        if p in df.columns:
            df[p] = pd.to_numeric(df[p], errors="coerce")
            df[p] = df.groupby("City")[p].ffill(limit=3)
            df[p] = df[p].fillna(df.groupby("City")[p].transform("median"))

    db_path = processed / "aqi_database.duckdb"
    con = duckdb.connect(str(db_path))
    con.execute("DROP TABLE IF EXISTS aqi_data")
    con.execute("CREATE TABLE aqi_data AS SELECT * FROM df")
    con.close()

    df.to_parquet(processed / "aqi_clean.parquet")
    return df
