FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app

# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy project files
COPY app/ app/
COPY urban_aqi/ urban_aqi/
COPY data/ data/
COPY models/ models/
COPY notebooks/ notebooks/
COPY scripts/ scripts/

# expose port for Streamlit
EXPOSE 7860

# run Streamlit app
CMD ["streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
