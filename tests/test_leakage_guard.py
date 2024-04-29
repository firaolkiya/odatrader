import pandas as pd
import pytest
from backend.backtesting.engine import BacktestEngine
from backend.backtesting.leakage_guard import LeakageGuard, LookaheadViolation, run_guarded_backtest


class TestLeakageGuard:
    def test_allows_valid_history(self):
        df = pd.DataFrame({"close": [100, 101, 102, 103]})
        guard = LeakageGuard()
        guard.set_bar(2)
        wrapped = guard.wrap(lambda row, prev, history=None: "HOLD")
        wrapped(df.iloc[2], df.iloc[1], history=df.iloc[:3])

    def test_blocks_oversized_history(self):
        guard = LeakageGuard()
        guard.set_bar(1)
        wrapped = guard.wrap(lambda row, prev, history=None: "HOLD")
        with pytest.raises(LookaheadViolation):
            wrapped(pd.Series({"close": 102}), pd.Series({"close": 101}), history=pd.DataFrame({"close": range(10)}))

    def test_guarded_backtest_runs(self):
        df = pd.DataFrame({"close": list(range(100, 120))})
        engine = BacktestEngine(initial_balance=1000)

        def sig(row, prev, history=None):
            return "BUY" if history is not None and len(history) == 10 else None

        result = run_guarded_backtest(engine, df, sig)
        assert result["final_balance"] >= 0
