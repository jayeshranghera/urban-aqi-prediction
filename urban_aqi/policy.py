"""Policy summary table for the dashboard."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def write_policy_summary(root: Path) -> pd.DataFrame:
    df = pd.read_parquet(root / "data/processed/aqi_clean.parquet")

    def _pm25_days(s: pd.Series) -> float:
        return float((s > 25).sum() / 24.0)

    def _no2_days(s: pd.Series) -> float:
        return float((s > 120).sum() / 24.0)

    compliance = (
        df.groupby("City", as_index=False)
        .agg(
            Days_Over_PM25_Limit=("PM2.5", _pm25_days),
            Days_Over_NO2_Limit=("NO2", _no2_days),
        )
        .sort_values("City")
    )

    out = root / "data/processed/policy_summary.csv"
    compliance.to_csv(out, index=False)
    return compliance
