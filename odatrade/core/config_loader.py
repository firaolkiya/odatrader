"""YAML configuration loader."""
import yaml
from pathlib import Path

def load_strategy_config(path: str = "config/strategies.yaml") -> dict:
    p = Path(path)
    if not p.exists():
        return {}
    with open(p) as f:
        return yaml.safe_load(f) or {}
