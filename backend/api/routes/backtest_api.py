"""Backtest API routes."""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/backtest", tags=["backtest"])

class BacktestRequest(BaseModel):
    symbol: str = "btcusdt"
    strategy: str = "rsi"
    days: int = 30

@router.post("/run")
def run_backtest(req: BacktestRequest):
    return {"status": "queued", "job_id": f"bt-{req.symbol}-{req.strategy}", "days": req.days}

@router.get("/results/{job_id}")
def get_results(job_id: str):
    return {"job_id": job_id, "status": "completed", "metrics": {}}
