<div align="center">

# Urban AQI Prediction & Policy Dashboard

**ML-powered air quality forecasting for European cities — with EU policy compliance analysis**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://urban-aqi-prediction.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-ML%20Model-FF6600?style=flat)](https://xgboost.readthedocs.io/)
[![LightGBM](https://img.shields.io/badge/LightGBM-ML%20Model-02AFF1?style=flat)](https://lightgbm.readthedocs.io/)
[![DuckDB](https://img.shields.io/badge/DuckDB-SQL%20Engine-FFF000?style=flat&logo=duckdb&logoColor=black)](https://duckdb.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![Data: EEA](https://img.shields.io/badge/Data-European%20Environment%20Agency-004F9F?style=flat)](https://www.eea.europa.eu/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub last commit](https://img.shields.io/github/last-commit/jayeshranghera/urban-aqi-prediction)](https://github.com/jayeshranghera/urban-aqi-prediction/commits/main)

<br/>

> **"Air pollution causes 300,000+ premature deaths in Europe every year.**
> **This dashboard turns that data into decisions."**

<br/>

[**Live Demo**](https://urban-aqi-prediction.streamlit.app/) &nbsp;|&nbsp; [Notebooks](./notebooks/) &nbsp;|&nbsp; [Project Doc](./project_doc.txt) &nbsp;|&nbsp; 

</div>

---

## Table of Contents

- [Overview](#overview)
- [Why This Project](#why-this-project)
- [Live Dashboard](#live-dashboard)
- [Data Sources](#data-sources)
- [Tech Stack](#tech-stack)
- [ML Pipeline](#ml-pipeline--5-notebook-stages)
- [EU Policy Thresholds](#eu-aqi-policy-thresholds)
- [Project Structure](#project-structure)
- [Local Setup](#local-setup)
- [Docker Deployment](#docker-deployment)
- [Skills Demonstrated](#skills-demonstrated)

---

## Overview

**Urban AQI Prediction** is an end-to-end data science project that forecasts Air Quality Index (AQI) levels for major European cities using **official government sensor data** from the European Environment Agency (EEA). It combines:

- **~2.37 million rows** of real hourly pollution readings (PM2.5, PM10, NO2)
- **Meteorological data** from Open-Meteo (temperature, humidity, wind, pressure)
- **XGBoost / LightGBM** ML models for 7-day AQI forecasting
- **EU Clean Air Directive** compliance analysis and policy recommendations
- **DuckDB** SQL engine for analytical queries at scale
- **Streamlit** interactive dashboard designed for non-technical users

This project sits at the intersection of **environmental data science**, **public policy**, and **machine learning** — a rare combination in data science portfolios.

---

## Why This Project

Most people have no idea what the air outside means for their health. While AQI data is publicly available, it is buried in government portals, presented in raw numbers with no context, and never linked to actionable health advice.

This dashboard solves five specific problems:

| Problem | Solution |
|---|---|
| No 7-day AQI forecast available for EU cities | XGBoost regression model trained on EEA + weather data |
| Raw µg/m3 values are meaningless to the public | Plain-English health summaries per AQI category |
| No comparison between cities | Berlin vs Madrid side-by-side, all pollutants |
| EU threshold breaches are unreported | Policy compliance table: hours/days exceeding legal limits |
| Health guidance is scattered across PDFs | Single dashboard: "Is it safe to run outside today?" |

---

## Live Dashboard

**[urban-aqi-prediction.streamlit.app](https://urban-aqi-prediction.streamlit.app/)**

The dashboard has four pages:

```
Home              ->  City AQI gauge, current readings, today's safety status
7-Day Forecast    ->  Interactive Plotly chart, daily safety cards, best day to go outside
City Compare      ->  Berlin vs Madrid — pollution, compliance, seasonal trends
Policy & Health   ->  EU thresholds, health impact table, monthly heatmap
```

> **Deployed on:** Streamlit Community Cloud (free tier)
> **Docker-ready for:** Hugging Face Spaces, Railway, Render, or any VPS

---

## Data Sources

### 1. EEA Air Quality Data

| Parameter | Details |
|---|---|
| **Source** | [European Environment Agency (EEA)](https://www.eea.europa.eu/en/datamaps-and-data/explore-interactive-maps/european-air-quality-index-1) |
| **Cities** | Berlin (Germany), Madrid (Spain) |
| **Years** | 2022 and 2025 |
| **Frequency** | Hourly measurements |
| **Pollutants** | PM2.5, PM10, NO2 |
| **Format** | Apache Parquet |
| **Total Records** | ~2.37 million rows |
| **Stations** | 272 monitoring stations across both cities |

### 2. Open-Meteo Weather Data

| Variable | Why It Matters for AQI |
|---|---|
| Temperature (2m) | Higher temps accelerate O3 formation |
| Relative Humidity | Affects PM2.5 concentration and dispersion |
| Surface Pressure | Low pressure traps pollutants near ground level |
| Precipitation | Rain washes out particulate matter |
| Wind Speed (10m) | High wind disperses pollutants away from urban areas |

### 3. EU Policy Thresholds

Thresholds sourced from the **EU Clean Air Directive** and **WHO Guidelines 2021**, used for both model labelling and dashboard safety alerts.

---

## Tech Stack

```
Data Layer       ->  Python · Pandas · PyArrow · Parquet
Database         ->  DuckDB (SQL analytical queries)
ML Models        ->  XGBoost · LightGBM
Experiment Log   ->  Jupyter Notebooks (5-stage pipeline)
Dashboard        ->  Streamlit · Plotly
Deployment       ->  Streamlit Cloud · Docker (Hugging Face / Railway ready)
Version Control  ->  Git · GitHub
```

---

## ML Pipeline — 5 Notebook Stages

The project is structured as a **sequential pipeline**, where each notebook produces an output that feeds the next stage.

```
+----------+------------------------------+-----------------------+
|  Stage   |  Notebook                    |  Output               |
+----------+------------------------------+-----------------------+
|  01 EDA  |  01_eda.ipynb                |  merged_hourly_raw    |
|  02 Prep |  02_preprocessing.ipynb      |  aqi_clean + DuckDB   |
|  03 Feat |  03_features.ipynb           |  features.parquet     |
|  04 ML   |  04_modelling.ipynb          |  model.pkl            |
|  05 Pol  |  05_policy.ipynb             |  policy summaries     |
+----------+------------------------------+-----------------------+
```

### Notebook 01 — Exploratory Data Analysis
- Load all EEA parquet files from 4 folders (e1a_2022, e1a_2025, e2a_2022, e2a_2025)
- Map station IDs to city names (Berlin: `DEBE` prefix, Madrid: `SP_28` prefix)
- Map numeric pollutant codes to readable names (8=PM2.5, 7=PM10, 5=NO2)
- Filter to valid measurements only (Validity flag = 1 or 2)
- Merge EEA data with Open-Meteo weather on timestamp and city
- **Output:** `data/processed/merged_hourly_raw.parquet`

### Notebook 02 — Preprocessing + DuckDB
- Handle missing values via forward-fill and city-level median imputation
- Remove outliers using IQR-based filtering per pollutant per city
- Create `aqi_database.duckdb` and load clean data as a structured table
- Run SQL analytical queries: monthly averages, peak pollution hours, city comparisons
- Run EU threshold compliance queries
- **Output:** `data/processed/aqi_clean.parquet` + `aqi_database.duckdb`

### Notebook 03 — Feature Engineering
- Time-based features: hour of day, day of week, month, season, is_weekend
- Lag features: PM2.5 at t-1h, t-2h, t-3h, t-6h, t-12h, t-24h
- Rolling mean features: 3h, 6h, 12h, 24h rolling averages
- AQI category label from EU thresholds (Good / Moderate / Poor / Very Poor / Extremely Poor)
- Binary target: will PM2.5 exceed 25 µg/m3 in the next 24h?
- **Output:** `data/processed/features.parquet`

### Notebook 04 — ML Modelling
- Time-based train/test split: **2022 = train · 2025 = test**
- XGBoost regression for 7-day hourly AQI forecast
- LightGBM as comparison model
- Evaluation metrics: MAE, RMSE, R2
- Feature importance analysis
- **Output:** `models/model.pkl` + `models/model_metadata.json`

### Notebook 05 — Policy Analysis
- EU Clean Air Directive compliance per city
- Monthly and hourly threshold breach patterns
- City ranking by annual average PM2.5
- Berlin vs Madrid cross-pollutant comparison
- **Output:** Policy recommendation summaries for dashboard

---

## EU AQI Policy Thresholds

Thresholds used for labelling, compliance analysis, and dashboard safety alerts.

| Pollutant | Good | Moderate | Poor | Very Poor | Extremely Poor |
|---|---|---|---|---|---|
| **PM2.5** (µg/m3) | <= 10 | 10–20 | 20–25 | 25–50 | > 50 |
| **PM10** (µg/m3) | <= 20 | 20–35 | 35–50 | 50–100 | > 100 |
| **NO2** (µg/m3) | <= 40 | 40–90 | 90–120 | 120–230 | > 230 |

*Based on EU Clean Air Directive (2008/50/EC) and WHO Air Quality Guidelines 2021*

---

## Project Structure

```
urban-aqi-prediction/
|
+-- app/
|   +-- app.py                    <- Streamlit main app (Home + AQI gauge)
|   +-- pages/
|       +-- 01_forecast.py        <- 7-day forecast page
|       +-- 02_compare.py         <- Berlin vs Madrid comparison
|       +-- 03_policy.py          <- Policy & health impact page
|
+-- data/
|   +-- raw/
|   |   +-- eea/unzipped/         <- EEA parquet files (e1a_2022, e2a_2025...)
|   |   +-- weather/              <- Open-Meteo CSVs (Berlin, Madrid)
|   |   +-- rules/                <- EU threshold CSV
|   +-- processed/
|       +-- merged_hourly_raw.parquet
|       +-- aqi_clean.parquet
|       +-- aqi_database.duckdb
|       +-- features.parquet
|
+-- models/
|   +-- model.pkl                 <- Trained XGBoost / LightGBM model
|   +-- model_metadata.json       <- Training params, metrics, feature list
|
+-- notebooks/
|   +-- 01_eda.ipynb
|   +-- 02_preprocessing.ipynb
|   +-- 03_features.ipynb
|   +-- 04_modelling.ipynb
|   +-- 05_policy.ipynb
|
+-- scripts/
|   +-- download_datasets.py      <- EEA + Open-Meteo data downloader
|
+-- Dockerfile                    <- Docker config (Hugging Face / Railway ready)
+-- requirements.txt
+-- generate_nbs.py
+-- README.md
```

---

## Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/jayeshranghera/urban-aqi-prediction.git
cd urban-aqi-prediction

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the Streamlit app
streamlit run app/app.py
```

Visit `http://localhost:8501` in your browser.

---

## Docker Deployment

The project includes a `Dockerfile` and is ready for deployment on **Hugging Face Spaces**, **Railway**, **Render**, or any Docker-compatible host.

```bash
# Build the image
docker build -t urban-aqi-prediction .

# Run locally
docker run -p 8501:8501 urban-aqi-prediction
```

Visit `http://localhost:8501`.

> **Note for Hugging Face Spaces:** HF Spaces expects port `7860`. Update the CMD in `Dockerfile` to `--server.port=7860` before deploying there.

**Currently deployed on:** [Streamlit Community Cloud](https://urban-aqi-prediction.streamlit.app/) (free tier)

---

## Skills Demonstrated

| Skill | How |
|---|---|
| **Real data ingestion** | EEA official government API, Parquet format, multi-folder pipeline |
| **Data cleaning** | Validity flag filtering, IQR outlier removal, missing value imputation |
| **SQL / Data Engineering** | DuckDB database creation, analytical SQL queries at scale |
| **Feature Engineering** | Lag features, rolling means, time-based cyclical features |
| **Machine Learning** | XGBoost + LightGBM regression, time-series train/test split, evaluation metrics |
| **Policy Analysis** | EU Clean Air Directive compliance, threshold breach detection |
| **Visualization** | Streamlit multi-page dashboard, Plotly interactive charts, AQI gauges |
| **Deployment** | Streamlit Cloud (live), Docker (Hugging Face / Railway ready) |
| **Domain Knowledge** | Air quality science, EU environmental policy, public health |
| **Communication** | Dashboard designed for non-technical users — plain English safety alerts |

---

## Author

**Jayesh Ranghera**
Data Analyst · Portfolio Project · March 2026

[![GitHub](https://img.shields.io/badge/GitHub-jayeshranghera-181717?style=flat&logo=github)](https://github.com/jayeshranghera)

---

<div align="center">

*Built with real EEA government data · Deployed on Streamlit Cloud · Docker-ready for HF Spaces*

**Star this repo if you found it useful!**

</div>
