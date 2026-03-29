"""Streamlit data loaders (reads artefacts produced by `urban_aqi` / `scripts/run_pipeline.py`)."""

from __future__ import annotations

import json
import pickle
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from urban_aqi.config import CITY_META, CITY_ORDER  # noqa: E402

CITIES_WITH_AQ = list(CITY_ORDER)


def project_paths_ok() -> tuple[bool, list[str]]:
    missing: list[str] = []
    for rel in (
        "models/model.pkl",
        "models/model_metadata.json",
        "data/processed/features.parquet",
        "data/processed/aqi_clean.parquet",
        "data/raw/rules/eu_aqi_policy_thresholds.csv",
    ):
        if not (ROOT / rel).is_file():
            missing.append(rel)
    return len(missing) == 0, missing


@st.cache_resource
def load_model_bundle() -> tuple[Any, dict[str, Any]]:
    with (ROOT / "models" / "model.pkl").open("rb") as f:
        model = pickle.load(f)
    with (ROOT / "models" / "model_metadata.json").open(encoding="utf-8") as f:
        meta = json.load(f)
    return model, meta


@st.cache_data
def load_features() -> pd.DataFrame:
    return pd.read_parquet(ROOT / "data" / "processed" / "features.parquet")


@st.cache_data
def load_aqi_clean() -> pd.DataFrame:
    return pd.read_parquet(ROOT / "data" / "processed" / "aqi_clean.parquet")


@st.cache_data
def load_policy_rules() -> pd.DataFrame:
    return pd.read_csv(ROOT / "data" / "raw" / "rules" / "eu_aqi_policy_thresholds.csv")


@st.cache_data
def load_policy_summary() -> pd.DataFrame | None:
    p = ROOT / "data" / "processed" / "policy_summary.csv"
    if not p.is_file():
        return None
    return pd.read_csv(p)


def pm25_band(value: float) -> tuple[str, str]:
    if value <= 10:
        return "good", "Good"
    if value <= 20:
        return "moderate", "Moderate"
    if value <= 25:
        return "poor", "Poor"
    if value <= 50:
        return "very_poor", "Very Poor"
    return "extremely_poor", "Extremely Poor"


def pm10_band(value: float) -> tuple[str, str]:
    if value <= 20:
        return "good", "Good"
    if value <= 35:
        return "moderate", "Moderate"
    if value <= 50:
        return "poor", "Poor"
    if value <= 100:
        return "very_poor", "Very Poor"
    return "extremely_poor", "Extremely Poor"


def no2_band(value: float) -> tuple[str, str]:
    if value <= 40:
        return "good", "Good"
    if value <= 90:
        return "moderate", "Moderate"
    if value <= 120:
        return "poor", "Poor"
    if value <= 230:
        return "very_poor", "Very Poor"
    return "extremely_poor", "Extremely Poor"


def latest_row(city: str) -> pd.Series | None:
    df = load_aqi_clean()
    sub = df[df["City"] == city].sort_values("Start")
    if sub.empty:
        return None
    return sub.iloc[-1]


def city_annual_means() -> pd.DataFrame:
    df = load_aqi_clean()
    out = (
        df.groupby("City", as_index=False)
        .agg(
            PM2_5_mean=("PM2.5", "mean"),
            PM10_mean=("PM10", "mean"),
            NO2_mean=("NO2", "mean"),
        )
        .sort_values("City")
    )
    return out


def forecast_last_seven_days(city: str) -> pd.DataFrame | None:
    model, meta = load_model_bundle()
    feats: list[str] = meta["features"]
    df = load_features()
    test = df[df["Start"].dt.year == 2025]
    sub = test[test["City"] == city].sort_values("Start")
    if sub.empty:
        return None
    window = sub.tail(7 * 24)
    if len(window) < 168:
        window = sub.tail(min(len(sub), 7 * 24))
    w = window.copy()
    w["pred_PM25_24h"] = model.predict(w[feats])
    w["date"] = w["Start"].dt.normalize()
    daily = (
        w.groupby("date", as_index=False)
        .agg(
            pred_PM25=("pred_PM25_24h", "mean"),
            actual_PM25=("target_PM25_24h", "mean"),
        )
        .sort_values("date")
    )
    return daily


def plain_summary(city: str, pm25: float) -> str:
    _, label = pm25_band(pm25)
    if pm25 <= 10:
        return f"Air quality in {city} is **{label}**. Outdoor activity is generally suitable for all groups."
    if pm25 <= 20:
        return (
            f"Air quality in {city} is **{label}**. People with respiratory sensitivity should limit prolonged exertion outdoors."
        )
    if pm25 <= 25:
        return (
            f"Air quality in {city} is **{label}**. Children and at-risk groups should shorten strenuous outdoor activity."
        )
    return (
        f"Air quality in {city} is **{label}**. Reduce heavy outdoor exercise; vulnerable groups should favour indoor air when possible."
    )


def data_source_line(city: str) -> str:
    src = CITY_META.get(city, {}).get("pollution_source", "See project documentation")
    return str(src)
