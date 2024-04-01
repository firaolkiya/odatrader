"""Strategy management API."""
from fastapi import APIRouter
from backend.strategies.registry import StrategyRegistry

router = APIRouter(prefix="/strategies", tags=["strategies"])

@router.get("/")
def list_strategies():
    return {"strategies": StrategyRegistry.list_all()}

@router.get("/{name}/config")
def get_config(name: str):
    return StrategyRegistry.get_config(name)
