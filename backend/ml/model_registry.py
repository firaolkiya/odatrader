"""ML model version registry."""
from typing import Dict
from datetime import datetime, timezone

class ModelRegistry:
    _models: Dict[str, Dict] = {}

    @classmethod
    def register(cls, name: str, path: str, version: str, metrics: dict = None):
        cls._models[name] = {"path": path, "version": version, "metrics": metrics or {}, "registered_at": datetime.now(timezone.utc).isoformat()}

    @classmethod
    def get(cls, name: str):
        return cls._models.get(name)

    @classmethod
    def list_models(cls):
        return cls._models
