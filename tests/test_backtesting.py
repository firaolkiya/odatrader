import pytest
import pandas as pd
import numpy as np
from backend.backtesting.engine import BacktestEngine
from backend.backtesting.monte_carlo import MonteCarloSimulator
from backend.backtesting.walk_forward import WalkForwardTester
from backend.backtesting.metrics import compute_metrics

class TestBacktestEngine:
    def test_initial_balance(self):
        e = BacktestEngine(5000)
        assert e.balance == 5000

    def test_run_generates_equity(self, sample_ohlcv_df):
        e = BacktestEngine(5000)
        def sig(r, p):
            return "BUY" if r["close"] > p["close"] else "SELL"
        r = e.run(sample_ohlcv_df, sig)
        assert len(e.equity_curve) > 1

    def test_no_trades_flat_signal(self, flat_df):
        e = BacktestEngine(5000)
        r = e.run(flat_df, lambda r, p: "HOLD")
        assert r["trades"] == 0

class TestMonteCarlo:
    def test_basic(self):
        r = MonteCarloSimulator(n_simulations=100).run([1,-0.5,2,-1,0.5])
        assert "median_final" in r

    def test_empty_trades(self):
        r = MonteCarloSimulator().run([])
        assert "error" in r

    def test_prob_profit(self):
        r = MonteCarloSimulator(n_simulations=500).run([1,1,1,-0.1])
        assert r["prob_profit"] > 0.5

    @pytest.mark.parametrize("n", [100, 500, 1000])
    def test_simulation_counts(self, n):
        r = MonteCarloSimulator(n_simulations=n).run([1,-0.5,1])
        assert r["n_simulations"] == n

class TestWalkForward:
    def test_runs_windows(self, sample_ohlcv_df):
        wf = WalkForwardTester()
        r = wf.run(sample_ohlcv_df, lambda r, p: "BUY", n_windows=2)
        assert r["n_windows"] >= 1

class TestMetrics:
    def test_compute_basic(self):
        eq = [5000, 5100, 5050, 5200]
        m = compute_metrics(eq, [100, -50, 150])
        assert "sharpe" in m

    def test_empty_equity(self):
        m = compute_metrics([5000], [])
        assert m["total_trades"] == 0
