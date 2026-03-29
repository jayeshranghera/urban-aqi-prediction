import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

APP_DIR = Path(__file__).resolve().parent.parent
ROOT = APP_DIR.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(APP_DIR))

from aqi_data import city_annual_means, project_paths_ok  # noqa: E402

st.set_page_config(page_title="Compare cities", layout="wide")

st.title("Cross-city means")

ok, missing = project_paths_ok()
if not ok:
    st.error("Missing processed air-quality data.")
    st.code("\n".join(missing))
    st.stop()

st.caption(
    "Full-series means from `aqi_clean.parquet` after preprocessing. Berlin and Madrid are EEA-based; Paris and Rome use Open-Meteo air-quality fields — interpret cross-city gaps as indicative, not like-for-like monitoring-network comparisons."
)

df = city_annual_means()
if df.empty:
    st.warning("No aggregated data.")
    st.stop()

fig = px.bar(
    df,
    x="City",
    y=["PM2_5_mean", "PM10_mean", "NO2_mean"],
    barmode="group",
    labels={
        "value": "µg/m³ (mean)",
        "variable": "Metric",
    },
)
fig.update_layout(
    title="Mean PM2.5, PM10, and NO2",
    legend_title_text="",
)
st.plotly_chart(fig, use_container_width=True)

st.dataframe(df.round(3), use_container_width=True, hide_index=True)

rank = df.sort_values("PM2_5_mean", ascending=False).reset_index(drop=True)
hi, lo = rank.iloc[0], rank.iloc[-1]
st.subheader("Summary")
st.info(
    f"**Highest** mean PM2.5 in this build: **{hi['City']}** ({hi['PM2_5_mean']:.2f} µg/m³). "
    f"**Lowest**: **{lo['City']}** ({lo['PM2_5_mean']:.2f} µg/m³). "
    "See the Policy page for EU-oriented concentration bands."
)
