"""Ensemble ML predictor."""
from typing import Dict, List

class EnsemblePredictor:
    def __init__(self, models: Dict[str, object], weights: Dict[str, float] = None):
        self.models = models
        self.weights = weights or {k: 1.0 / len(models) for k in models}

    def predict(self, features) -> float:
        total = sum(self.models[name].predict(features) * self.weights[name] for name in self.models)
        return total
