"""Combine EEA pivoted series with Open-Meteo (AQ + weather) for Paris and Rome."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from urban_aqi.config import CITY_META
from urban_aqi.eea import load_eea_pivoted
from urban_aqi.openmeteo_series import load_weather_csv, merge_weather_and_aq


def _align_columns(df: pd.DataFrame) -> pd.DataFrame:
    want = [
        "Start",
        "City",
        "NO2",
        "O3",
        "PM10",
        "PM2.5",
        "temperature_2m",
        "relative_humidity_2m",
        "surface_pressure",
        "precipitation",
        "wind_speed_10m",
    ]
    for c in want:
        if c not in df.columns:
            df[c] = float("nan")
    return df[want]


def build_merged_hourly_raw(
    root: Path,
    *,
    force_aq_download: bool = False,
) -> pd.DataFrame:
    # EEA provides hourly pollutant concentrations (PM2.5/PM10/NO2/O3).
    # For Berlin and Madrid we must also merge Open-Meteo weather so the
    # downstream feature builder has a non-null weather feature set.
    eea = load_eea_pivoted(root / "data/raw/eea/unzipped")

    aq_dir = root / "data/raw/openmeteo_aq"

    # Weather-only merge for EEA cities
    weather_berlin = load_weather_csv(
        root / "data/raw/weather/openmeteo_berlin_2022-01-01_2025-12-31.csv",
        "Berlin",
    )
    berlin = (
        pd.merge(
            eea[eea["City"] == "Berlin"],
            weather_berlin,
            left_on=["Start", "City"],
            right_on=["time", "City"],
            how="inner",
        )
        .drop(columns=["time"])
    )
    berlin = _align_columns(berlin)

    weather_madrid = load_weather_csv(
        root / "data/raw/weather/openmeteo_madrid_2022-01-01_2025-12-31.csv",
        "Madrid",
    )
    madrid = (
        pd.merge(
            eea[eea["City"] == "Madrid"],
            weather_madrid,
            left_on=["Start", "City"],
            right_on=["time", "City"],
            how="inner",
        )
        .drop(columns=["time"])
    )
    madrid = _align_columns(madrid)

    paris = merge_weather_and_aq(
        "Paris",
        float(CITY_META["Paris"]["lat"]),  # type: ignore[arg-type]
        float(CITY_META["Paris"]["lon"]),  # type: ignore[arg-type]
        root / "data/raw/weather/openmeteo_paris_2022-01-01_2025-12-31.csv",
        aq_dir / "paris_hourly.parquet",
        force_aq_download,
    )
    rome = merge_weather_and_aq(
        "Rome",
        float(CITY_META["Rome"]["lat"]),  # type: ignore[arg-type]
        float(CITY_META["Rome"]["lon"]),  # type: ignore[arg-type]
        root / "data/raw/weather/openmeteo_rome_2022-01-01_2025-12-31.csv",
        aq_dir / "rome_hourly.parquet",
        force_aq_download,
    )
    paris = _align_columns(paris)
    rome = _align_columns(rome)

    out = pd.concat([berlin, madrid, paris, rome], ignore_index=True)
    out["Start"] = pd.to_datetime(out["Start"])
    out = out.sort_values(["City", "Start"]).reset_index(drop=True)
    return out
