import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_healthz():
    r = client.get('/healthz')
    assert r.status_code == 200
    assert r.json()['status'] == 'ok'

def test_predict_contract(monkeypatch):
    # patch model_service to avoid real pickle
    from app import main
    class Dummy:
        def predict_one(self, text):
            return "positive", 0.95
    main.model_service = Dummy()

    r = client.post('/predict', json={'review': 'This product is amazing!'})
    assert r.status_code == 200
    body = r.json()
    assert set(body.keys()) == {'sentiment', 'confidence'}
    assert body['sentiment'] == 'positive'
    assert 0.0 <= body['confidence'] <= 1.0

def test_metrics_exposed():
    r = client.get('/metrics')
    assert r.status_code == 200
    assert "predictions_total" in r.text
