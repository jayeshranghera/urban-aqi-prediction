#!/usr/bin/env python3
"""Download all EEA + weather data for Urban AQI project.

Cities: Berlin, Madrid, Paris, Rome
Outputs:
  data/raw/eea/eea_e2a_2022_all_cities.zip
  data/raw/eea/eea_e1a_2025_all_cities.zip
  data/raw/weather/openmeteo_<city>_2022_2025.csv
  data/raw/rules/eu_aqi_policy_thresholds.csv
"""

from pathlib import Path
import csv
import time
import requests

ROOT      = Path(__file__).resolve().parent.parent
EEA_DIR   = ROOT / "data" / "raw" / "eea"
WEATHER_DIR = ROOT / "data" / "raw" / "weather"
RULES_DIR = ROOT / "data" / "raw" / "rules"

EEA_API_URL = "https://eeadmz1-downloads-api-appservice.azurewebsites.net/ParquetFile"

CITIES = {
    "berlin": {"name": "Berlin", "country": "DE", "lat": 52.52,   "lon": 13.405},
    "madrid": {"name": "Madrid", "country": "ES", "lat": 40.4168, "lon": -3.7038},
    "paris":  {"name": "Paris",  "country": "FR", "lat": 48.8566, "lon": 2.3522},
    "rome":   {"name": "Rome",   "country": "IT", "lat": 41.9028, "lon": 12.4964},
}

POLLUTANTS = ["PM2.5", "PM10", "NO2", "O3"]

WEATHER_VARS = [
    "temperature_2m",
    "relative_humidity_2m",
    "surface_pressure",
    "precipitation",
    "wind_speed_10m",
]


def ensure_dirs() -> None:
    EEA_DIR.mkdir(parents=True, exist_ok=True)
    WEATHER_DIR.mkdir(parents=True, exist_ok=True)
    RULES_DIR.mkdir(parents=True, exist_ok=True)


def download_eea_zip(dataset: int, start: str, end: str, outfile: Path) -> bool:
    """Download EEA parquet zip. Returns True on success."""
    if outfile.exists():
        print(f"  Already exists: {outfile.name} — skipping")
        return True

    payload = {
        "countries": [c["country"] for c in CITIES.values()],
        "cities":    [c["name"]    for c in CITIES.values()],
        "pollutants": POLLUTANTS,
        "dataset":   dataset,
        "dateTimeStart": start,
        "dateTimeEnd":   end,
        "aggregationType": "hour",
        "source": "Customscript",
    }

    print(f"\nRequesting EEA dataset={dataset} ({start[:4]}) ...")
    print(f"  Countries: {payload['countries']}")
    print(f"  Cities   : {payload['cities']}")
    print(f"  Pollutants: {payload['pollutants']}")

    try:
        response = requests.post(EEA_API_URL, json=payload, timeout=600)
        response.raise_for_status()

        size_mb = len(response.content) / (1024 * 1024)
        if size_mb < 0.01:
            print(f"  WARNING: Response too small ({size_mb:.3f} MB) — API may have returned no data")
            print(f"  Response text: {response.text[:300]}")
            return False

        outfile.write_bytes(response.content)
        print(f"  Saved: {outfile.name} ({size_mb:.2f} MB)")
        return True

    except requests.exceptions.Timeout:
        print("  ERROR: Request timed out (600s). EEA API is slow — try again.")
        return False
    except requests.exceptions.RequestException as e:
        print(f"  ERROR: {e}")
        return False


def download_weather_csv(city_key: str, start_date: str, end_date: str) -> bool:
    """Download Open-Meteo historical weather. Returns True on success."""
    city    = CITIES[city_key]
    outfile = WEATHER_DIR / f"openmeteo_{city_key}_{start_date}_{end_date}.csv"

    if outfile.exists():
        print(f"  Already exists: {outfile.name} — skipping")
        return True

    params = {
        "latitude":   city["lat"],
        "longitude":  city["lon"],
        "start_date": start_date,
        "end_date":   end_date,
        "hourly":     ",".join(WEATHER_VARS),
        "timezone":   "UTC",
        "format":     "csv",
    }

    print(f"  Downloading weather: {city['name']} ({start_date} to {end_date})")
    try:
        response = requests.get(
            "https://archive-api.open-meteo.com/v1/archive",
            params=params,
            timeout=120,
        )
        response.raise_for_status()
        outfile.write_text(response.text, encoding="utf-8")
        size_kb = outfile.stat().st_size / 1024
        print(f"    Saved: {outfile.name} ({size_kb:.0f} KB)")
        return True

    except requests.exceptions.RequestException as e:
        print(f"    ERROR: {e}")
        return False


def write_policy_rules() -> None:
    """Write EU AQI policy threshold CSV."""
    rows = [
        ["metric", "good_max", "moderate_max", "poor_max", "very_poor_max", "extremely_poor_min"],
        ["PM2.5_ug_m3",  10,  20,  25,  50,  50],
        ["PM10_ug_m3",   20,  35,  50, 100, 100],
        ["NO2_ug_m3",    40,  90, 120, 230, 230],
        ["O3_ug_m3",     50, 100, 130, 240, 240],
    ]
    out = RULES_DIR / "eu_aqi_policy_thresholds.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)
    print(f"  Saved: {out.name}")


def main() -> None:
    print("=" * 55)
    print("  Urban AQI — dataset downloader")
    print(f"  Cities: {', '.join(c['name'] for c in CITIES.values())}")
    print("=" * 55)

    ensure_dirs()

    # ── EEA air quality data ──────────────────────────────────
    print("\n[1/3] EEA air quality data")
    ok1 = download_eea_zip(
        dataset=2,
        start="2022-01-01T00:00:00Z",
        end="2022-12-31T23:59:59Z",
        outfile=EEA_DIR / "eea_e2a_2022_all_cities.zip",
    )
    time.sleep(3)   # be polite to the API

    ok2 = download_eea_zip(
        dataset=1,
        start="2025-01-01T00:00:00Z",
        end="2025-12-31T23:59:59Z",
        outfile=EEA_DIR / "eea_e1a_2025_all_cities.zip",
    )

    # ── Weather data ─────────────────────────────────────────
    print("\n[2/3] Open-Meteo weather data")
    for city_key in CITIES:
        download_weather_csv(city_key, "2022-01-01", "2025-12-31")

    # ── Policy rules ─────────────────────────────────────────
    print("\n[3/3] EU AQI policy thresholds")
    write_policy_rules()

    # ── Summary ──────────────────────────────────────────────
    print("\n" + "=" * 55)
    if ok1 and ok2:
        print("  All downloads completed successfully.")
        print("\n  Next step:")
        print("  1. Unzip EEA files into data/raw/eea/unzipped/")
        print("     eea_e2a_2022_all_cities.zip -> e2a_2022/")
        print("     eea_e1a_2025_all_cities.zip -> e1a_2025/")
        print("  2. Run notebooks/01_eda.ipynb")
    else:
        print("  Some downloads failed — check errors above.")
    print("=" * 55)


if __name__ == "__main__":
    main()
