"""Signals API with SignalSnapshot output."""
from fastapi import APIRouter, Query
from typing import Optional
import pandas as pd

router = APIRouter(prefix="/signals", tags=["signals"])

_latest_snapshots: dict = {}


@router.get("/")
def get_signals(symbol: Optional[str] = None):
    if symbol and symbol in _latest_snapshots:
        return _latest_snapshots[symbol]
    return {"signals": list(_latest_snapshots.values())}


@router.get("/evaluate/{symbol}")
def evaluate_symbol(symbol: str):
    try:
        from backend.engine.adaptive_voter import AdaptiveVoter
        from backend.db.postgres_pool import PostgresPool
        from config.config import DATABASE_URL
        voter = AdaptiveVoter(symbol)
        pool = PostgresPool(DATABASE_URL)
        if pool.connect():
            from backend.db.repositories.market import MarketDataRepository
            repo = MarketDataRepository(pool)
            df = repo.get_candles(symbol, limit=100)
        else:
            df = pd.DataFrame()
        if df.empty:
            import numpy as np
            df = pd.DataFrame({"close": np.random.randn(50).cumsum() + 100,
                               "high": np.random.randn(50).cumsum() + 101,
                               "low": np.random.randn(50).cumsum() + 99,
                               "open": np.random.randn(50).cumsum() + 100,
                               "volume": np.random.rand(50) * 100})
        snap = voter.evaluate(df)
        _latest_snapshots[symbol] = snap.to_dict()
        return snap.to_dict()
    except Exception as e:
        return {"error": str(e), "symbol": symbol}
