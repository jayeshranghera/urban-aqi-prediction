# Urban AQI Prediction

Production-style portfolio project that combines **machine learning**, **environmental data engineering**, and **policy communication** for urban air quality.

The application forecasts and explains air-quality conditions for **Berlin, Madrid, Paris, and Rome** using a reproducible pipeline and an interactive **Streamlit** dashboard.

**Author:** Jayesh Ranghera

## Project Highlights

- End-to-end hourly pipeline: ingestion, preprocessing, feature engineering, model training, policy summary
- Transparent multi-source design with explicit data provenance
- `XGBoost` model for 24-hour-ahead PM2.5 prediction
- Policy-facing communication layer using EU-oriented concentration bands
- Dashboard optimized for non-technical and policy audiences

## Data Provenance

| City | Air quality source | Weather source |
|------|--------------------|----------------|
| Berlin, Madrid | EEA hourly parquet exports (`data/raw/eea/unzipped/`) | Open-Meteo historical weather CSV |
| Paris, Rome | Open-Meteo Air Quality API (CAMS European fields) | Open-Meteo historical weather CSV |

Notes:
- The bundled EEA extract in this repository includes Germany and Madrid-region Spain only.
- Paris and Rome are therefore integrated through Open-Meteo CAMS-based air-quality fields.
- This mixed-source design is disclosed in-app and in documentation for interpretation clarity.

## Repository Structure

| Path | Purpose |
|------|---------|
| `urban_aqi/` | Core pipeline modules (merge, preprocess, features, train, policy) |
| `scripts/run_pipeline.py` | One-command rebuild for processed data + model + policy outputs |
| `scripts/download_datasets.py` | EEA/weather download helper script |
| `app/` | Streamlit application (`app.py`, pages, shared loaders) |
| `data/processed/` | Pipeline outputs (`merged`, `clean`, `features`, `policy`) |
| `models/` | Trained model artifact and metadata |
| `notebooks/` | Stage-wise notebooks (`01` to `05`) aligned with package logic |
| `Dockerfile` | Containerized deployment configuration |

## Quickstart

### 1) Install dependencies

```bash
pip install -r requirements.txt
```

### 2) Build all artifacts

```bash
python scripts/run_pipeline.py
```

Optional refresh for Paris/Rome AQ cache:

```bash
python scripts/run_pipeline.py --force-aq-download
```

### 3) Run dashboard

```bash
python -m streamlit run app/app.py
```

## Model and Outputs

- Model: `XGBoost` regressor (`models/model.pkl`)
- Metadata: `models/model_metadata.json` (feature list + error metrics)
- Policy export: `data/processed/policy_summary.csv`
- Database export: `data/processed/aqi_database.duckdb`

## Reproducibility

- The canonical pipeline lives in `urban_aqi/`
- Notebooks are intentionally thin and call the same underlying logic
- This keeps experimentation, scripted runs, and deployment behavior consistent

## Deployment

The project is Docker-ready and suitable for platforms such as Hugging Face Spaces or any container host supporting Python/Streamlit workloads.

## Attribution and License Notes

- EEA data usage: [EEA Legal Notice](https://www.eea.europa.eu/en/legal-notice)
- Open-Meteo: [open-meteo.com](https://open-meteo.com/)
- CAMS program: [atmosphere.copernicus.eu](https://atmosphere.copernicus.eu/)

## Maintainer

- **Name:** Jayesh Ranghera
- **GitHub:** [jayeshranghera](https://github.com/jayeshranghera)
- **LinkedIn:** [Add your LinkedIn URL](https://www.linkedin.com/)
- **Portfolio:** [Add your portfolio URL](https://example.com)
- **Email:** [Add your email](mailto:your.email@example.com)
