FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1     MODEL_URL="https://github.com/Profession-AI/progetti-devops/raw/refs/heads/main/Deploy%20e%20monitoraggio%20di%20un%20modello%20di%20sentiment%20analysis%20per%20recensioni/sentimentanalysismodel.pkl"     MODEL_PATH="/app/model/sentiment.pkl"     LOG_LEVEL="info"     SERVICE_NAME="model-api"     PORT=8000

# deps for scientific stack
RUN apt-get update && apt-get install -y --no-install-recommends     build-essential curl ca-certificates gcc g++ make     libopenblas-dev &&     rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# copy app
COPY app ./app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
