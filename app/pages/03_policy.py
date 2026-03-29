import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Policy & Health", layout="centered")

st.title("EU Clean Air Directive & Public Health")

st.write("### The Legal Limits")
st.write("The European Union has strict policy frameworks governing local air quality. When cities consistently breach these limits, they risk infringement procedures from the European Commission.")

data = {
    'Pollutant': ['PM2.5', 'PM10', 'NO2', 'O3'],
    'Good': ['≤ 10', '≤ 20', '≤ 40', '≤ 50'],
    'Moderate': ['10 - 20', '20 - 35', '40 - 90', '50 - 100'],
    'Poor': ['20 - 25', '35 - 50', '90 - 120', '100 - 130']
}
df_rules = pd.DataFrame(data)

st.table(df_rules)

st.write("### Precautionary Advice")
st.warning("**For Moderate Days**: Asthmatic individuals or those with respiratory issues should limit strenuous outdoor activity.")
st.error("**For Poor Days**: The general public should avoid prolonged outdoor exercise, and vulnerable groups must stay indoors.")

st.write("### Policy Recommendations")
st.success("For cities like Madrid and Paris struggling with NO2: Accelerate Low Emission Zone (LEZ) adoption. For cities suffering PM spikes: Manage industrial and construction dust protocols during drought weeks.")
