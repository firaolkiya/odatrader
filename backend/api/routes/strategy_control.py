"""Strategy start/stop control API."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from backend.auth.middleware import require_auth

router = APIRouter(prefix="/strategy", tags=["strategy-control"])
_running_strategies: set = set()


class StrategyControl(BaseModel):
    name: str


@router.post("/start", dependencies=[Depends(require_auth)])
def start_strategy(req: StrategyControl):
    _running_strategies.add(req.name)
    return {"started": req.name, "running": list(_running_strategies)}


@router.post("/stop", dependencies=[Depends(require_auth)])
def stop_strategy(req: StrategyControl):
    _running_strategies.discard(req.name)
    return {"stopped": req.name, "running": list(_running_strategies)}


@router.get("/status")
def strategy_status():
    return {"running": list(_running_strategies)}
