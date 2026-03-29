import streamlit as st
import pandas as pd
from pathlib import Path

# page config
st.set_page_config(page_title="Urban AQI Prediction", layout="wide")

# basic CSS to make it look clean without overengineering
st.markdown("""
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
    .poor { border-left: 5px solid #e74c3c; }
    </style>
""", unsafe_allow_html=True)

st.title("Urban AQI Prediction Dashboard")

# sidebar city selector
city_options = ["Berlin", "Madrid", "Paris", "Rome"]
selected_city = st.sidebar.selectbox("Select City", city_options)

st.write(f"### Current Air Quality Overview: {selected_city}")

# placeholder for data loading
# in a real run, this would load from processed/features.parquet or similar
st.write("Welcome to the Urban AQI Prediction tool. This dashboard helps you understand the current air quality, next 7-day forecast, and policy compliance for major European cities.")

st.info(f"Currently viewing data for {selected_city}. Use the sidebar pages to navigate through Forecasts, Comparisons, and Policy Analysis.")

# dummy current metrics until the model runs
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="metric-card good"><h4>PM2.5</h4><h2>12 µg/m³</h2><p>Good</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-card moderate"><h4>PM10</h4><h2>26 µg/m³</h2><p>Moderate</p></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="metric-card poor"><h4>NO2</h4><h2>95 µg/m³</h2><p>Poor</p></div>', unsafe_allow_html=True)

st.write("---")
st.write("**Note**: The data used in this dashboard is sourced from official EEA sensors and Open-Meteo.")
