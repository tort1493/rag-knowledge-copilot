from dataclasses import dataclass
import numpy as np

@dataclass
class Prediction:
    score: float
    label: int

def predict(features: np.ndarray) -> Prediction:
    # TODO: load a real model, run inference, return a Prediction.
    score = float(np.clip(features.mean(), 0, 1))
    label = int(score >= 0.5)
    return Prediction(score=score, label=label)
