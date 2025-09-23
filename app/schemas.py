from pydantic import BaseModel, Field

class PredictRequest(BaseModel):
    review: str = Field(..., min_length=1, description="English review text")

class PredictResponse(BaseModel):
    sentiment: str
    confidence: float
