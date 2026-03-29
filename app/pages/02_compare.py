import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="City Comparison", layout="wide")
st.title("Berlin vs Madrid vs Paris vs Rome")

st.write("This page demonstrates the comparative air quality statistics for the analyzed cities.")

# fake data for dashboard staging before models generate proper DBs
data = {
    'City': ['Berlin', 'Madrid', 'Paris', 'Rome'],
    'Average PM2.5 (Annual)': [14, 21, 19, 24],
    'Average NO2 (Annual)': [38, 55, 60, 48]
}

df_compare = pd.DataFrame(data)

st.subheader("Annual Average Pollutants")

# bar chart showing comparisons per city
fig = px.bar(df_compare, x='City', y=['Average PM2.5 (Annual)', 'Average NO2 (Annual)'], barmode='group')
st.plotly_chart(fig, use_container_width=True)

st.write("---")
st.subheader("Key Insight (Baseline)")
st.info("Based on exploratory historical data, Paris and Madrid typically show higher NO2 levels from dense inner-city traffic compared to Berlin. Rome experiences summer peaks for PM10 due to temperature inversions.")
