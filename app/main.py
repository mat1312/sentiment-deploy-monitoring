import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, generate_latest, multiprocess
from .schemas import PredictRequest, PredictResponse
from .model import get_service
from .metrics import PREDICTIONS_TOTAL, PREDICTION_ERRORS_TOTAL, timed

SERVICE_NAME = os.getenv('SERVICE_NAME', 'model-api')

app = FastAPI(
    title="Sentiment Analysis API",
    description="Predict sentiment (positive/negative/neutral) for English reviews.",
    version="1.0.0"
)

# Load model service once at startup
model_service = get_service()

@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": SERVICE_NAME}

@app.post("/predict", response_model=PredictResponse)
@timed('POST', '/predict')
def predict(payload: PredictRequest):
    text = payload.review
    try:
        label, conf = model_service.predict_one(text)
        PREDICTIONS_TOTAL.labels(status='success').inc()
        return PredictResponse(sentiment=label, confidence=round(conf, 4))
    except Exception as e:
        PREDICTION_ERRORS_TOTAL.inc()
        PREDICTIONS_TOTAL.labels(status='error').inc()
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

@app.get("/metrics")
def metrics():
    # single-process default registry
    data = generate_latest()
    return PlainTextResponse(data.decode('utf-8'), media_type=CONTENT_TYPE_LATEST)

@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code >= 500:
        PREDICTION_ERRORS_TOTAL.inc()
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
