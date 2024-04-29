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
    import uuid
    job_id = f"bt-{req.symbol}-{uuid.uuid4().hex[:8]}"
    try:
        import pandas as pd
        import numpy as np
        from backend.backtesting.replay import ReplayBacktester
        df = pd.DataFrame({
            "close": np.random.randn(req.days * 24 * 60).cumsum() + 50000,
            "high": np.random.randn(req.days * 24 * 60).cumsum() + 50100,
            "low": np.random.randn(req.days * 24 * 60).cumsum() + 49900,
            "open": np.random.randn(req.days * 24 * 60).cumsum() + 50000,
            "volume": np.random.rand(req.days * 24 * 60) * 100,
        })
        bt = ReplayBacktester(req.symbol)
        results = bt.run(df)
        from backend.storage.parquet_store import ParquetStore
        ParquetStore().save_backtest(job_id, results)
        return {"status": "completed", "job_id": job_id, "trades": results["trades"],
                "final_balance": results["final_balance"]}
    except Exception as e:
        return {"status": "error", "job_id": job_id, "error": str(e)}

@router.post("/walk-forward")
def run_walk_forward(req: BacktestRequest):
    import pandas as pd
    import numpy as np
    from backend.backtesting.walk_forward import WalkForwardTester
    df = pd.DataFrame({"close": np.random.randn(1000).cumsum() + 100,
                       "high": np.random.randn(1000).cumsum() + 101,
                       "low": np.random.randn(1000).cumsum() + 99,
                       "open": np.random.randn(1000).cumsum() + 100,
                       "volume": np.random.rand(1000)})
    wf = WalkForwardTester()
    return wf.run(df, lambda r, p: "BUY" if r.get("close", 0) > p.get("close", 0) else "SELL")

@router.post("/monte-carlo")
def run_monte_carlo(pnls: list = None):
    from backend.backtesting.monte_carlo import MonteCarloSimulator
    pnls = pnls or [1.5, -0.8, 2.1, -1.2, 0.5, 3.0, -2.0, 1.0]
    return MonteCarloSimulator().run(pnls)

@router.get("/results/{job_id}")
def get_results(job_id: str):
    from backend.storage.parquet_store import ParquetStore
    store = ParquetStore()
    return {"job_id": job_id, "status": "completed", "backtests": store.list_backtests()}
