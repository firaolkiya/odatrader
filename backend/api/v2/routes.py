"""OdaTrade API v2."""
from fastapi import APIRouter

router = APIRouter(prefix="/api/v2", tags=["OdaTrade v2"])

@router.get("/status")
def v2_status():
    return {"version": "2.0", "name": "OdaTrade", "features": ["backtest", "scanner", "alerts", "ml"]}
