import sys
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).resolve().parent.parent
ROOT = APP_DIR.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(APP_DIR))

from aqi_data import load_policy_rules, load_policy_summary, project_paths_ok  # noqa: E402

st.set_page_config(page_title="Policy & health", layout="wide")

st.title("EU-oriented bands and health messaging")

ok, missing = project_paths_ok()
if not ok:
    st.error("Missing policy rules.")
    st.code("\n".join(missing))
    st.stop()

st.markdown(
    "### Concentration bands (`eu_aqi_policy_thresholds.csv`)"
)
st.caption(
    "These CSV values drive categorical colouring in the app. They support risk communication; **legal compliance** uses official limit values, averaging periods, and approved measurement methods."
)

rules = load_policy_rules()
display = rules.rename(
    columns={
        "metric": "Metric",
        "good_max": "Good — upper bound (µg/m³)",
        "moderate_max": "Moderate — upper bound",
        "poor_max": "Poor — upper bound",
        "very_poor_max": "Very poor — upper bound",
        "extremely_poor_min": "Extremely poor — from (µg/m³)",
    }
)
st.dataframe(display, use_container_width=True, hide_index=True)

st.markdown("### Indicative exceedances (`policy_summary.csv`)")
summary = load_policy_summary()
if summary is not None and not summary.empty:
    st.dataframe(summary.round(2), use_container_width=True, hide_index=True)
    st.caption(
        "Counts scale hourly threshold breaches by 24 to approximate **day-equivalents** for dashboard use only."
    )
else:
    st.info("Run `python scripts/run_pipeline.py` or notebook `05_policy.ipynb` to generate `policy_summary.csv`.")

st.markdown("### Public-health style guidance")
st.warning(
    "**Moderate and above (sensitive groups):** limit prolonged vigorous outdoor activity when pollution is elevated."
)
st.error(
    "**Poor and above:** shorten time outdoors for everyone; vulnerable groups should prioritise indoor environments when feasible."
)

st.success(
    "**Policy angle:** NO2 is often traffic-linked (low-emission zones, fleet turnover); PM episodes may track meteorology and regional sources — pair forecasts with local authority advisories."
)
