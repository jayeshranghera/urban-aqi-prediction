#!/usr/bin/env python3
"""Rebuild processed datasets, model, and policy tables (same logic as notebooks)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from urban_aqi.pipeline import run_all  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser(description="Run Urban AQI pipeline")
    p.add_argument(
        "--force-aq-download",
        action="store_true",
        help="Re-download Paris/Rome air quality from Open-Meteo (overwrites cache)",
    )
    args = p.parse_args()
    out = run_all(force_aq_download=args.force_aq_download)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
