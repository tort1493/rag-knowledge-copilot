from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
from project.model import predict

app = FastAPI(title="AI Project API", version="0.1.0")

class PredictRequest(BaseModel):
    features: list[float]

class PredictResponse(BaseModel):
    score: float
    label: int

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict", response_model=PredictResponse)
def do_predict(req: PredictRequest):
    x = np.array(req.features, dtype=float)
    out = predict(x)
    return PredictResponse(score=out.score, label=out.label)
