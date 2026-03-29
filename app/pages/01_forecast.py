import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

APP_DIR = Path(__file__).resolve().parent.parent
ROOT = APP_DIR.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(APP_DIR))

from aqi_data import (  # noqa: E402
    CITIES_WITH_AQ,
    forecast_last_seven_days,
    load_model_bundle,
    pm25_band,
    project_paths_ok,
)

st.set_page_config(page_title="Forecast", layout="wide")

st.title("Model validation — seven-day window")

ok, missing = project_paths_ok()
if not ok:
    st.error("Missing model or feature files.")
    st.code("\n".join(missing))
    st.stop()

_, meta = load_model_bundle()
city = st.sidebar.selectbox("City", CITIES_WITH_AQ)

st.write(
    "**24 h ahead PM2.5 (µg/m³).** The chart aggregates hourly predictions to **daily means** over the "
    "most recent **7×24 h** segment in the **2025** hold-out year, matching the train/test split in `urban_aqi/train.py`."
)
st.caption(
    f"Hold-out MAE ≈ {meta.get('mae', 0):.2f} µg/m³ · RMSE ≈ {meta.get('rmse', 0):.2f} µg/m³ · "
    f"Features: {', '.join(meta.get('features', []))}"
)

daily = forecast_last_seven_days(city)
if daily is None or daily.empty:
    st.warning("No 2025 rows for this city.")
    st.stop()

fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=daily["date"],
        y=daily["pred_PM25"],
        name="Predicted (daily mean of 24 h-ahead)",
        mode="lines+markers",
        line=dict(color="#3498db"),
    )
)
fig.add_trace(
    go.Scatter(
        x=daily["date"],
        y=daily["actual_PM25"],
        name="Actual target (24 h-ahead)",
        mode="lines+markers",
        line=dict(color="#95a5a6", dash="dash"),
    )
)
fig.add_hline(
    y=25,
    line_dash="dash",
    line_color="red",
    annotation_text="Reference: 25 µg/m³ (upper end of “Poor” band for PM2.5 in project rules)",
)
fig.update_layout(
    title=f"Daily mean PM2.5 — {city}",
    xaxis_title="Date (UTC)",
    yaxis_title="µg/m³",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Narrative by day")
for _, r in daily.iterrows():
    d = pd.Timestamp(r["date"])
    pred = float(r["pred_PM25"])
    _, lab = pm25_band(pred)
    day_str = d.strftime("%A, %d %b %Y")
    if pred > 25:
        st.error(
            f"**{day_str}** — Mean predicted PM2.5 **{pred:.1f} µg/m³** ({lab}). Limit prolonged outdoor exertion; at-risk groups reduce activity."
        )
    elif pred > 20:
        st.warning(
            f"**{day_str}** — Mean predicted PM2.5 **{pred:.1f} µg/m³** ({lab}). Sensitive groups should limit strenuous outdoor activity."
        )
    else:
        st.success(
            f"**{day_str}** — Mean predicted PM2.5 **{pred:.1f} µg/m³** ({lab}). Generally acceptable for outdoor exercise; check personal sensitivity."
        )
