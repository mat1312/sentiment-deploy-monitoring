# Deploy & Monitor Sentiment Analysis (FastAPI + Jenkins + Prometheus/Grafana)

Questo progetto dimostra **deploy** e **monitoraggio** di un modello di Sentiment Analysis per recensioni in inglese.
Comprende API FastAPI, pipeline Jenkins, Docker/Compose, Prometheus, Grafana e (opzionale) manifest Kubernetes.

## Requisiti
- Docker e Docker Compose
- (Opzionale) Jenkins con Docker in Docker o agent con Docker CLI
- Python 3.11 se vuoi eseguire i test localmente
- Accesso Internet per scaricare il modello pickle dal repo

## Avvio rapido (Docker Compose)
```bash
# 1) build & run API + Prometheus + Grafana + cAdvisor + Node Exporter
docker compose up -d

# 2) API docs
open http://localhost:8000/docs   # (Windows: start / Mac: open)

# 3) Grafana (user: admin / pass: admin, impostato nel compose)
open http://localhost:3000
# Dashboard: "Sentiment API – Overview"
```

## Variabili d'ambiente principali
- `MODEL_URL` (default: link raw GitHub) – URL del modello pickle (english only)
- `MODEL_PATH` (default: `/app/model/sentiment.pkl`) – path locale dove salvare il modello
- `LOG_LEVEL`  (default: `info`)
- `SERVICE_NAME` (default: `model-api`)

## Test locali
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pytest -q
```

## Pipeline Jenkins (riassunto)
- **Build & Test**: esegue lint/pytest
- **Build Docker**: crea immagine `sentiment-api:${GIT_COMMIT}`
- **Push** (solo main): invia a un registry (Docker Hub/GHCR)
- **Deploy**: aggiorna servizio su host via SSH (Compose) o su Kubernetes

Vedi `Jenkinsfile` per dettagli e variabili.

## Note su metriche
- `/metrics` espone tempi di risposta, conteggi, errori (Prometheus).
- CPU/Mem via **cAdvisor** e **Node Exporter** (compose inclusi).
- Dashboard Grafana auto-provisionata (Prometheus datasource).

## Kubernetes (opzionale)
Manifest in `k8s/` con Deployment, Service e annotazioni Prometheus.
