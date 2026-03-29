import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="7-Day Forecast", layout="wide")

st.title("7-Day AQI Forecast")

cities = ["Berlin", "Madrid", "Paris", "Rome"]
city = st.sidebar.selectbox("Select City", cities)

# this is where we would load our ML model predictions
st.write(f"Showing the forecasted Air Quality Index levels for **{city}** based on our XGBoost model.")

# fake some predictions for the visualization at this level
dates = pd.date_range(start=pd.Timestamp.today(), periods=7)
preds_pm25 = np.random.randint(10, 40, size=7)

df_forecast = pd.DataFrame({
    'Date': dates,
    'Predicted PM2.5': preds_pm25
})

# simple chart using plotly
fig = px.line(df_forecast, x='Date', y='Predicted PM2.5', markers=True, title=f"PM2.5 Forecast - {city}")
# add simple horizontal lines for EU limits
fig.add_hline(y=25, line_dash="dash", line_color="red", annotation_text="EU Daily Limit")
st.plotly_chart(fig, use_container_width=True)

# recommendations
st.subheader("Daily Insights")
for i, row in df_forecast.iterrows():
    if row['Predicted PM2.5'] > 25:
        st.error(f"{row['Date'].strftime('%A, %b %d')}: Poor Air Quality. Wear a mask if going out.")
    else:
        st.success(f"{row['Date'].strftime('%A, %b %d')}: Safe to exercise outdoors.")
