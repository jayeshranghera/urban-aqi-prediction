"""End-to-end orchestration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from urban_aqi.features import build_features
from urban_aqi.merge_hourly import build_merged_hourly_raw
from urban_aqi.paths import project_root
from urban_aqi.policy import write_policy_summary
from urban_aqi.preprocess import preprocess_merged
from urban_aqi.train import train_and_save


def run_all(*, force_aq_download: bool = False) -> dict[str, Any]:
    root = project_root()
    merged = build_merged_hourly_raw(root, force_aq_download=force_aq_download)
    merged.to_parquet(root / "data/processed/merged_hourly_raw.parquet")

    clean = preprocess_merged(merged, root)
    feats = build_features(clean, root)
    meta = train_and_save(root)
    policy = write_policy_summary(root)
    return {
        "root": str(root),
        "merged_rows": len(merged),
        "features_rows": len(feats),
        "model_metrics": meta,
        "policy_cities": policy["City"].tolist(),
    }
