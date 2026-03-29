"""Project constants: cities, coordinates, date span."""

from __future__ import annotations

# Order used in dashboards and reports
CITY_ORDER: tuple[str, ...] = ("Berlin", "Madrid", "Paris", "Rome")

CITY_META: dict[str, dict[str, object]] = {
    "Berlin": {
        "pollution_source": "EEA in-situ (hourly parquet)",
        "lat": 52.52,
        "lon": 13.405,
    },
    "Madrid": {
        "pollution_source": "EEA in-situ (hourly parquet)",
        "lat": 40.4168,
        "lon": -3.7038,
    },
    "Paris": {
        "pollution_source": "Open-Meteo Air Quality API (CAMS European analysis/forecast blend)",
        "lat": 48.8566,
        "lon": 2.3522,
    },
    "Rome": {
        "pollution_source": "Open-Meteo Air Quality API (CAMS European analysis/forecast blend)",
        "lat": 41.9028,
        "lon": 12.4964,
    },
}

WEATHER_START = "2022-01-01"
WEATHER_END = "2025-12-31"

AQ_YEAR_WINDOWS: tuple[tuple[str, str], ...] = (
    ("2022-01-01", "2022-12-31"),
    ("2023-01-01", "2023-12-31"),
    ("2024-01-01", "2024-12-31"),
    ("2025-01-01", "2025-12-31"),
)
