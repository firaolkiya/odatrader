"""Hot-reload configuration API."""
import os
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from backend.auth.middleware import require_auth

router = APIRouter(prefix="/config", tags=["config"])

_runtime_config: dict = {}


class ConfigPatch(BaseModel):
    path: str
    value: object


@router.get("/")
def get_config():
    import yaml
    configs = {}
    for fname in ["config/strategies.yaml", "config/instruments.yaml", "config/adaptive.yaml"]:
        if os.path.exists(fname):
            with open(fname) as f:
                configs[fname] = yaml.safe_load(f)
    configs["runtime"] = _runtime_config
    return configs


@router.patch("/", dependencies=[Depends(require_auth)])
def patch_config(patch: ConfigPatch):
    keys = patch.path.split(".")
    target = _runtime_config
    for k in keys[:-1]:
        target = target.setdefault(k, {})
    target[keys[-1]] = patch.value
    if patch.path.startswith("strategy."):
        from backend.audit.decision_logger import DecisionLogger
        DecisionLogger()._write("config_change", {"path": patch.path, "value": patch.value})
    return {"patched": patch.path, "value": patch.value}


@router.post("/mode", dependencies=[Depends(require_auth)])
def set_trading_mode(mode: str):
    if mode not in ("paper", "live"):
        return {"error": "mode must be paper or live"}
    os.environ["TRADING_MODE"] = mode
    try:
        from backend.api.routes.orders_api import get_exec_router
        get_exec_router().set_mode(mode)
    except Exception:
        pass
    return {"mode": mode}
