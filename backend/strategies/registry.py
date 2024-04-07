"""Pluggable strategy registry."""
from typing import Dict, Type, Any

class StrategyRegistry:
    _strategies: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register(cls, name: str, strategy_class: Type, config: dict = None):
        cls._strategies[name] = {"class": strategy_class, "config": config or {}}

    @classmethod
    def list_all(cls):
        return list(cls._strategies.keys())

    @classmethod
    def get_config(cls, name: str):
        return cls._strategies.get(name, {}).get("config", {})

    @classmethod
    def get(cls, name: str):
        entry = cls._strategies.get(name)
        return entry["class"]() if entry else None
