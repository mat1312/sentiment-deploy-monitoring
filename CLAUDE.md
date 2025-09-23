# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a sentiment analysis API deployment and monitoring project that combines FastAPI, Docker, Prometheus, Grafana, and Jenkins for MLOps. The API predicts sentiment (positive/negative/neutral) for English reviews using a pre-trained scikit-learn model.

## Commands

### Development
```bash
# Local development with auto-reload
make dev
# or
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run tests
make test
# or
pytest -q

# Run tests with coverage and JUnit XML (as in Jenkins)
pytest -q --junitxml=reports/test-results.xml
```

### Docker & Deployment
```bash
# Build Docker image locally
make docker-build
# or
docker build -t sentiment-api:local .

# Start full stack (API + Prometheus + Grafana)
make compose-up
# or
docker compose up -d

# Stop stack
make compose-down
# or
docker compose down
```

## Architecture

### Core Components
- **FastAPI Application** (`app/main.py`): Main API with `/predict`, `/healthz`, `/metrics` endpoints
- **Model Service** (`app/model.py`): Downloads and loads pickle model from GitHub, handles predictions
- **Metrics** (`app/metrics.py`): Prometheus metrics (request latency, prediction counts, errors)
- **Schemas** (`app/schemas.py`): Pydantic models for request/response validation

### Model Loading
The application downloads a pre-trained sentiment analysis model from GitHub on startup. The model URL is configurable via `MODEL_URL` environment variable. Model is cached locally at `MODEL_PATH` (default: `/app/model/sentiment.pkl`).

### Monitoring Stack
- **Prometheus**: Scrapes metrics from API `/metrics` endpoint
- **Grafana**: Visualizes metrics with pre-configured dashboard
- **cAdvisor & Node Exporter**: System metrics (configured in docker-compose.yml)

### CI/CD Pipeline
Jenkins pipeline (`Jenkinsfile`) performs:
1. Python virtual environment setup and testing
2. Docker image build with git commit tag
3. Push to registry (main branch only)
4. SSH deployment to remote host via Docker Compose

## Environment Variables
- `MODEL_URL`: URL to download the pickle model (default: GitHub raw URL)
- `MODEL_PATH`: Local path to store model (default: `/app/model/sentiment.pkl`)
- `LOG_LEVEL`: Logging level (default: `info`)
- `SERVICE_NAME`: Service name for health checks (default: `model-api`)

## Testing
Tests use FastAPI TestClient with model service mocking to avoid loading the actual pickle file. Key test areas:
- Health endpoint functionality
- Prediction endpoint contract validation
- Metrics endpoint exposure

## Deployment Options
1. **Docker Compose**: Local/single-host deployment with monitoring stack
2. **Kubernetes**: Manifests in `k8s/` directory with Prometheus annotations
3. **Jenkins**: Automated CI/CD with SSH deployment to remote Docker host