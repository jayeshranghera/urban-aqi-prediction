"""Open-Meteo weather CSV + Air Quality API merged to the same schema as EEA rows."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

from urban_aqi.config import AQ_YEAR_WINDOWS

AQ_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"


def load_weather_csv(path: Path, city: str) -> pd.DataFrame:
    w = pd.read_csv(path, skiprows=3)
    w.columns = [c.split(" ")[0] for c in w.columns]
    w["City"] = city
    w["time"] = pd.to_datetime(w["time"])
    return w


def fetch_air_quality_hourly(lat: float, lon: float) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for start, end in AQ_YEAR_WINDOWS:
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "pm2_5,pm10,nitrogen_dioxide,ozone",
            "start_date": start,
            "end_date": end,
            "timezone": "UTC",
        }
        r = requests.get(AQ_URL, params=params, timeout=180)
        r.raise_for_status()
        data = r.json()
        h = data["hourly"]
        frames.append(
            pd.DataFrame(
                {
                    "Start": pd.to_datetime(h["time"]),
                    "PM2.5": h["pm2_5"],
                    "PM10": h["pm10"],
                    "NO2": h["nitrogen_dioxide"],
                    "O3": h["ozone"],
                }
            )
        )
    return pd.concat(frames, ignore_index=True)


def merge_weather_and_aq(
    city: str,
    lat: float,
    lon: float,
    weather_csv: Path,
    cache_parquet: Path | None,
    force_download: bool,
) -> pd.DataFrame:
    weather = load_weather_csv(weather_csv, city)
    if cache_parquet and cache_parquet.is_file() and not force_download:
        aq = pd.read_parquet(cache_parquet)
        if "City" not in aq.columns:
            aq["City"] = city
    else:
        aq = fetch_air_quality_hourly(lat, lon)
        if cache_parquet:
            cache_parquet.parent.mkdir(parents=True, exist_ok=True)
            aq.to_parquet(cache_parquet)

    aq["City"] = city

    merged = pd.merge(
        aq,
        weather,
        left_on=["Start", "City"],
        right_on=["time", "City"],
        how="inner",
    )
    merged = merged.drop(columns=["time"])
    return merged
