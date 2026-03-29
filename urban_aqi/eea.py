"""Load and pivot EEA hourly parquet exports (Berlin, Madrid)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def samplingpoint_to_city(samplingpoint: str) -> str | None:
    s = str(samplingpoint)
    if s.startswith("DE/") or "DEBE" in s:
        return "Berlin"
    if s.startswith("ES/") and "SP_28" in s:
        return "Madrid"
    return None


def load_eea_pivoted(unzipped_dir: Path) -> pd.DataFrame:
    files = list(unzipped_dir.glob("**/*.parquet"))
    if not files:
        raise FileNotFoundError(f"No parquet under {unzipped_dir}")

    chunks: list[pd.DataFrame] = []
    for f in files:
        tmp = pd.read_parquet(f)
        tmp["_source_file"] = f.name
        chunks.append(tmp)

    df_eea = pd.concat(chunks, ignore_index=True)
    df_eea["City"] = df_eea["Samplingpoint"].map(samplingpoint_to_city)
    df_eea = df_eea[df_eea["City"].notna()].copy()

    df_eea = df_eea[df_eea["Validity"].isin([1, 2])]

    pol_map = {8: "PM2.5", 7: "PM10", 5: "NO2", 6001: "O3"}
    df_eea["Pollutant_Name"] = df_eea["Pollutant"].map(pol_map)
    df_eea = df_eea.dropna(subset=["Pollutant_Name"])

    df_eea["Start"] = pd.to_datetime(df_eea["Start"])
    df_pivoted = (
        df_eea.pivot_table(
            index=["Start", "City"],
            columns="Pollutant_Name",
            values="Value",
            aggfunc="mean",
        )
        .reset_index()
    )
    return df_pivoted
