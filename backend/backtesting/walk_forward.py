"""Walk-forward backtesting with train/validate/test splits."""
import logging
from typing import Callable, Dict, List
import pandas as pd
from backend.backtesting.engine import BacktestEngine
from backend.backtesting.metrics import compute_metrics
from backend.backtesting.leakage_guard import run_guarded_backtest
from backend.exec.fee_model import FeeModel

logger = logging.getLogger("odatrade.walk_forward")


class WalkForwardTester:
    def __init__(self, train_pct: float = 0.6, validate_pct: float = 0.2, initial_balance: float = 5000.0):
        self.train_pct = train_pct
        self.validate_pct = validate_pct
        self.initial_balance = initial_balance
        self.fee_model = FeeModel()

    def run(self, df: pd.DataFrame, signal_fn: Callable, n_windows: int = 3) -> Dict:
        results = []
        window_size = len(df) // n_windows
        for i in range(n_windows):
            start = i * window_size
            end = min((i + 1) * window_size, len(df))
            window_df = df.iloc[start:end].copy()
            if len(window_df) < 50:
                continue
            train_end = int(len(window_df) * self.train_pct)
            test_df = window_df.iloc[train_end:]
            engine = BacktestEngine(initial_balance=self.initial_balance)
            result = run_guarded_backtest(engine, test_df, signal_fn)
            pnls = [t["pnl"] for t in engine.trades]
            metrics = compute_metrics(engine.equity_curve, pnls)
            results.append({
                "window": i, "trades": result["trades"],
                "final_balance": result["final_balance"], "metrics": metrics,
            })
            logger.info("Walk-forward window %d: trades=%d sharpe=%.2f", i, result["trades"], metrics.get("sharpe", 0))
        return {"windows": results, "n_windows": len(results)}
