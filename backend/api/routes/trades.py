"""Trade history API routes."""
from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter(prefix="/trades", tags=["trades"])

@router.get("/")
def list_trades(symbol: Optional[str] = None, limit: int = Query(50, le=500)):
    return {"trades": [], "symbol": symbol, "limit": limit}

@router.get("/stats")
def trade_stats():
    return {"total": 0, "win_rate": 0.0, "avg_pnl": 0.0}
