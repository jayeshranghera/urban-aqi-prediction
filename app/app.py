import sys
from pathlib import Path

import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
ROOT = APP_DIR.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(APP_DIR))

from aqi_data import (  # noqa: E402
    CITIES_WITH_AQ,
    data_source_line,
    latest_row,
    no2_band,
    plain_summary,
    pm10_band,
    pm25_band,
    project_paths_ok,
)

st.set_page_config(page_title="Urban AQI — Dashboard", layout="wide")

st.markdown(
    """
    <style>
    .metric-card {
        padding: 20px;
        border-radius: 8px;
        background-color: #2b2b2b;
        color: white;
        margin: 10px 0;
    }
    .good { border-left: 5px solid #2ecc71; }
    .moderate { border-left: 5px solid #f1c40f; }
    .poor { border-left: 5px solid #e67e22; }
    .very_poor { border-left: 5px solid #e74c3c; }
    .extremely_poor { border-left: 5px solid #9b59b6; }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("Urban air quality — overview")

ok, missing = project_paths_ok()
if not ok:
    st.error(
        "Required artefacts are missing. From the repository root, run `python scripts/run_pipeline.py`, "
        "or execute the notebooks in order (01 → 05)."
    )
    st.code("\n".join(missing))
    st.stop()

selected_city = st.sidebar.selectbox("City", CITIES_WITH_AQ)

st.subheader(f"Latest hour — {selected_city}")

st.caption(
    "Berlin and Madrid use **EEA** in-situ hourly measurements; Paris and Rome use **Open-Meteo** air-quality fields (CAMS European) "
    "at representative coordinates, each merged with **Open-Meteo** weather. Threshold bands follow `data/raw/rules/eu_aqi_policy_thresholds.csv`."
)

row = latest_row(selected_city)
if row is None:
    st.warning(f"No rows found for {selected_city}.")
    st.stop()

last_ts = pd.Timestamp(row["Start"])
st.caption(
    f"Timestamp (UTC): **{last_ts.strftime('%Y-%m-%d %H:%M')}** · {data_source_line(selected_city)}"
)

p25, p10, n2 = float(row["PM2.5"]), float(row["PM10"]), float(row["NO2"])
k25, lab25 = pm25_band(p25)
k10, lab10 = pm10_band(p10)
kn2, labn2 = no2_band(n2)

st.markdown(plain_summary(selected_city, p25))

cards = [
    (k25, "PM2.5", f"{p25:.1f} µg/m³", lab25),
    (k10, "PM10", f"{p10:.1f} µg/m³", lab10),
    (kn2, "NO2", f"{n2:.1f} µg/m³", labn2),
]
cols = st.columns(3)
for col, (k, title, val, lab) in zip(cols, cards):
    with col:
        st.markdown(
            f'<div class="metric-card {k}"><h4>{title}</h4><h2>{val}</h2><p>{lab}</p></div>',
            unsafe_allow_html=True,
        )

st.divider()
st.caption(
    "Forecasts use an **XGBoost** model (24 h ahead PM2.5) trained on the shared feature table; see **Forecast** and **Policy** pages."
)
