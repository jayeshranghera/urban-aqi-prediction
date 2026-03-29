import json
from pathlib import Path

def create_notebook(filename, cells):
    nb = {
        "cells": [],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 5
    }
    for cell_type, source in cells:
        # source can be string or list of strings
        if isinstance(source, str):
            source = [line + '\n' for line in source.split('\n')]
            if source:
                source[-1] = source[-1].rstrip('\n') # remove last newline
        
        cell = {
            "cell_type": cell_type,
            "metadata": {},
            "source": source
        }
        if cell_type == "code":
            cell["outputs"] = []
            cell["execution_count"] = None
            
        nb["cells"].append(cell)
        
    with open(filename, 'w') as f:
        json.dump(nb, f, indent=1)

# ==========================================
# Notebook 1: EDA
# ==========================================
nb1_cells = [
    ("markdown", "# 01 — Exploratory Data Analysis\n**Urban AQI Prediction | Berlin, Madrid, Paris, Rome**"),
    ("code", '''import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

ROOT = Path().resolve().parents[0]
UNZIPPED = ROOT / 'data/raw/eea/unzipped'
WEATHER = ROOT / 'data/raw/weather'

# find all parquet files in nested folders
files = list(UNZIPPED.glob('**/*.parquet'))
print(f"Found {len(files)} parquet files.")'''),
    ("code", '''# load all files into a single dataframe
dfs = []
for f in files:
    tmp = pd.read_parquet(f)
    tmp['_source_file'] = f.name
    dfs.append(tmp)

df_eea = pd.concat(dfs, ignore_index=True)
print(f"Total EEA records: {df_eea.shape[0]:,}")'''),
    ("code", '''# automatically extract city based on known codes
def get_city(station: str) -> str:
    s = str(station)
    if 'DE' in s:
        return 'Berlin'
    elif 'ES' in s:
        return 'Madrid'
    # Automatically detecting FR and IT
    elif 'FR' in s:
        return 'Paris'
    elif 'IT' in s:
        return 'Rome'
    return 'Unknown'

df_eea['City'] = df_eea['Samplingpoint'].apply(get_city)
print("Measurements by city:")
print(df_eea['City'].value_counts())'''),
    ("code", '''# filter valid measurements only (1 or 2 means valid)
df_eea = df_eea[df_eea['Validity'].isin([1, 2])]
print(f"Valid records: {df_eea.shape[0]:,}")'''),
    ("code", '''# map pollutants
pol_map = {8: 'PM2.5', 7: 'PM10', 5: 'NO2', 6001: 'O3'}
df_eea['Pollutant_Name'] = df_eea['Pollutant'].map(pol_map)

# drop if not in our 4 targeted pollutants
df_eea = df_eea.dropna(subset=['Pollutant_Name'])
print(df_eea['Pollutant_Name'].value_counts())'''),
    ("code", '''# pivot the data so pollutants become columns
df_eea['Start'] = pd.to_datetime(df_eea['Start'])
# pivot table
df_pivoted = df_eea.pivot_table(
    index=['Start', 'City'], 
    columns='Pollutant_Name', 
    values='Value', 
    aggfunc='mean'
).reset_index()

print("Pivoted shape:", df_pivoted.shape)
df_pivoted.head()'''),
    ("code", '''# load weather data and merge
weather_files = list(WEATHER.glob('*.csv'))

dfs_w = []
for f in weather_files:
    # file format: openmeteo_berlin_2022-01-01_2025-12-31.csv
    # extract city from filename
    city_name = f.stem.split('_')[1].capitalize()
    
    # skip rows to read actual csv headers from openmeteo (first 3 rows are meta/blank)
    w_df = pd.read_csv(f, skiprows=3)
    # Strip units from column names (e.g. 'temperature_2m (°C)' -> 'temperature_2m')
    w_df.columns = [c.split(' ')[0] for c in w_df.columns]
    w_df['City'] = city_name
    dfs_w.append(w_df)

df_weather = pd.concat(dfs_w, ignore_index=True)
df_weather['time'] = pd.to_datetime(df_weather['time'])
print("Weather data shape:", df_weather.shape)'''),
    ("code", '''# Merge EEA and Weather
df_merged = pd.merge(
    df_pivoted, 
    df_weather, 
    left_on=['Start', 'City'], 
    right_on=['time', 'City'], 
    how='inner'
)
# clean up columns
df_merged = df_merged.drop(columns=['time'])

out_dir = ROOT / 'data/processed'
out_dir.mkdir(exist_ok=True)
df_merged.to_parquet(out_dir / 'merged_hourly_raw.parquet')
print("Saved to merged_hourly_raw.parquet")''')
]

# ==========================================
# Notebook 2: Preprocessing
# ==========================================
nb2_cells = [
    ("markdown", "# 02 — Preprocessing & DuckDB\nClean data & establish database."),
    ("code", '''import pandas as pd
import numpy as np
import duckdb
from pathlib import Path

ROOT = Path().resolve().parents[0]
processed_dir = ROOT / 'data/processed'

df = pd.read_parquet(processed_dir / 'merged_hourly_raw.parquet')
print("Loaded raw shape:", df.shape)'''),
    ("code", '''# handle missing values using ffill and city median
df['Start'] = pd.to_datetime(df['Start'])
df = df.sort_values(['City', 'Start'])

# fill gaps up to 3 hours with ffill
pollutants = ['PM2.5', 'PM10', 'NO2', 'O3']
for p in pollutants:
    if p in df.columns:
        df[p] = df.groupby('City')[p].ffill(limit=3)
        # fill remaining with median
        df[p] = df[p].fillna(df.groupby('City')[p].transform('median'))

print("Missing values handled.")'''),
    ("code", '''# duckdb setup
db_path = processed_dir / 'aqi_database.duckdb'
con = duckdb.connect(str(db_path))

# save to duckdb
con.execute("DROP TABLE IF EXISTS aqi_data")
con.execute("CREATE TABLE aqi_data AS SELECT * FROM df")

# run a quick test query
res = con.execute("SELECT City, AVG(\\"PM2.5\\") as avg_pm25 FROM aqi_data GROUP BY City").df()
print("DuckDB Query successful:\\n", res)
con.close()'''),
    ("code", '''# save clean parquet
df.to_parquet(processed_dir / 'aqi_clean.parquet')
print("Saved aqi_clean.parquet")''')
]

# ==========================================
# Notebook 3: Features
# ==========================================
nb3_cells = [
    ("markdown", "# 03 — Feature Engineering\nTime features, lags, targets."),
    ("code", '''import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path().resolve().parents[0]
df = pd.read_parquet(ROOT / 'data/processed/aqi_clean.parquet')
df = df.sort_values(['City', 'Start'])'''),
    ("code", '''# time features
df['hour'] = df['Start'].dt.hour
df['dayofweek'] = df['Start'].dt.dayofweek
df['month'] = df['Start'].dt.month
df['is_weekend'] = df['dayofweek'].isin([5, 6]).astype(int)'''),
    ("code", '''# lag features for PM2.5
df['PM25_lag1'] = df.groupby('City')['PM2.5'].shift(1)
df['PM25_lag24'] = df.groupby('City')['PM2.5'].shift(24)

# rolling mean
df['PM25_roll24'] = df.groupby('City')['PM2.5'].rolling(24, min_periods=1).mean().reset_index(level=0, drop=True)

# target: PM2.5 value 24 hours into the future
df['target_PM25_24h'] = df.groupby('City')['PM2.5'].shift(-24)

# drop NA rows resulting from shifts
df = df.dropna()
print("Features created. Shape:", df.shape)'''),
    ("code", '''df.to_parquet(ROOT / 'data/processed/features.parquet')
print("Saved features.parquet")''')
]

# ==========================================
# Notebook 4: Modelling
# ==========================================
nb4_cells = [
    ("markdown", "# 04 — ML Modelling\nTrain XGBoost per the project requirements."),
    ("code", '''import pandas as pd
import numpy as np
from pathlib import Path
import json
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
from xgboost import XGBRegressor

ROOT = Path().resolve().parents[0]
df = pd.read_parquet(ROOT / 'data/processed/features.parquet')'''),
    ("code", '''# time based split: train on 2022, test on 2025
train = df[df['Start'].dt.year == 2022]
test = df[df['Start'].dt.year == 2025]

# if dates are different, fallback to 80/20 split
if train.empty or test.empty:
    split_idx = int(len(df) * 0.8)
    train = df.iloc[:split_idx]
    test = df.iloc[split_idx:]

features = ['hour', 'dayofweek', 'month', 'is_weekend', 'PM25_lag1', 'PM25_lag24', 'PM25_roll24', 
            'temperature_2m', 'relative_humidity_2m', 'wind_speed_10m']
            
target = 'target_PM25_24h'

X_train, y_train = train[features], train[target]
X_test, y_test = test[features], test[target]
print(f"Train samples: {len(X_train)}, Test samples: {len(X_test)}")'''),
    ("code", '''# Train XGBoost
model = XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)
model.fit(X_train, y_train)

preds = model.predict(X_test)
mae = mean_absolute_error(y_test, preds)
rmse = root_mean_squared_error(y_test, preds)

print(f"MAE: {mae:.2f}")
print(f"RMSE: {rmse:.2f}")'''),
    ("code", '''# Save model
models_dir = ROOT / 'models'
models_dir.mkdir(exist_ok=True)

import pickle
with open(models_dir / 'model.pkl', 'wb') as f:
    pickle.dump(model, f)
    
meta = {"features": features, "mae": float(mae), "rmse": float(rmse)}
with open(models_dir / 'model_metadata.json', 'w') as f:
    json.dump(meta, f)
    
print("Model and metadata saved.")''')
]

# ==========================================
# Notebook 5: Policy
# ==========================================
nb5_cells = [
    ("markdown", "# 05 — Policy Analysis\nEU Clean Air Directive policy compliance checks."),
    ("code", '''import pandas as pd
from pathlib import Path

ROOT = Path().resolve().parents[0]
df = pd.read_parquet(ROOT / 'data/processed/aqi_clean.parquet')'''),
    ("code", '''# EU Thresholds logic
# PM2.5 > 25 is 'Poor', PM2.5 > 50 is 'Extremely Poor'
# Calculate compliance
compliance = df.groupby('City').apply(lambda x: pd.Series({
    'Days_Over_PM25_Limit': (x['PM2.5'] > 25).sum() / 24.0, # approximate days
    'Days_Over_NO2_Limit': (x['NO2'] > 120).sum() / 24.0
})).reset_index()

print("EU Limit Exceedances:")
display(compliance)'''),
    ("code", '''# saving policy baseline for dashboard
out = ROOT / 'data/processed/policy_summary.csv'
compliance.to_csv(out, index=False)
print("Saved policy summary.")''')
]

create_notebook("notebooks/01_eda.ipynb", nb1_cells)
create_notebook("notebooks/02_preprocessing.ipynb", nb2_cells)
create_notebook("notebooks/03_features.ipynb", nb3_cells)
create_notebook("notebooks/04_modelling.ipynb", nb4_cells)
create_notebook("notebooks/05_policy.ipynb", nb5_cells)

print("All notebooks generated successfully in notebooks/ folder.")
