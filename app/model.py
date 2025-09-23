import os
import pickle
import requests
from typing import Any, Dict, List, Tuple

DEFAULT_MODEL_URL = os.getenv('MODEL_URL', 'https://github.com/Profession-AI/progetti-devops/raw/refs/heads/main/Deploy%20e%20monitoraggio%20di%20un%20modello%20di%20sentiment%20analysis%20per%20recensioni/sentimentanalysismodel.pkl')
DEFAULT_MODEL_PATH = os.getenv('MODEL_PATH', '/app/model/sentiment.pkl')

os.makedirs(os.path.dirname(DEFAULT_MODEL_PATH), exist_ok=True)

class ModelService:
    def __init__(self, model: Any):
        self.model = model
        # best-effort classes
        self.classes = getattr(model, 'classes_', ['negative', 'neutral', 'positive'])

    def predict_one(self, text: str) -> Tuple[str, float]:
        # scikit pipeline usually accepts list[str]
        pred = self.model.predict([text])[0]
        # confidence
        confidence = 0.0
        proba = None
        if hasattr(self.model, 'predict_proba'):
            try:
                proba = self.model.predict_proba([text])[0]
            except Exception:
                proba = None
        if proba is not None and len(proba) == len(self.classes):
            # match predicted class index
            try:
                idx = list(self.classes).index(pred)
                confidence = float(proba[idx])
            except Exception:
                confidence = float(max(proba))
        else:
            # decision_function as fallback (SVM-like), normalize roughly to [0,1]
            if hasattr(self.model, 'decision_function'):
                try:
                    df = self.model.decision_function([text])
                    if hasattr(df, '__iter__'):
                        m = float(max(df[0]))
                        mn = float(min(df[0]))
                        confidence = (m - mn) / (abs(m) + abs(mn) + 1e-9)
                    else:
                        confidence = 0.5
                except Exception:
                    confidence = 0.5
            else:
                confidence = 0.5
        return str(pred), float(confidence)

def download_model(url: str = DEFAULT_MODEL_URL, dst: str = DEFAULT_MODEL_PATH) -> str:
    if os.path.exists(dst) and os.path.getsize(dst) > 0:
        return dst
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    with open(dst, 'wb') as f:
        f.write(resp.content)
    return dst

def load_model(path: str = DEFAULT_MODEL_PATH) -> Any:
    with open(path, 'rb') as f:
        return pickle.load(f)

def get_service() -> ModelService:
    # ensure file exists
    path = DEFAULT_MODEL_PATH
    url = DEFAULT_MODEL_URL
    try:
        path = download_model(url, path)
    except Exception:
        # allow running offline (tests), assuming file already present or tests patch load_model
        pass
    model = load_model(path)
    return ModelService(model)
