import pytest
from backend.portfolio.tracker import PortfolioTracker, Position
from backend.portfolio.analytics import sharpe_ratio, max_drawdown, win_rate
from backend.portfolio.pnl import calculate_trade_pnl

class TestPortfolioTracker:
    def test_initial_balance(self):
        t = PortfolioTracker(5000)
        assert t.balance == 5000

    def test_update_position(self):
        t = PortfolioTracker()
        t.update_position("btcusdt", 0.1, 50000)
        assert "btcusdt" in t.positions

    def test_get_summary(self):
        t = PortfolioTracker(5000)
        s = t.get_summary()
        assert s["balance"] == 5000

    def test_multiple_positions(self):
        t = PortfolioTracker()
        t.update_position("btc", 0.1, 50000)
        t.update_position("eth", 1.0, 3000)
        assert len(t.get_positions()) == 2

class TestAnalytics:
    def test_sharpe_positive(self):
        assert sharpe_ratio([0.01, 0.02, 0.01, 0.015]) > 0

    def test_sharpe_single_return(self):
        assert sharpe_ratio([0.01]) == 0

    def test_max_drawdown(self):
        dd = max_drawdown([100, 110, 90, 95])
        assert dd > 0

    def test_max_drawdown_no_loss(self):
        assert max_drawdown([100, 110, 120]) == 0

    def test_win_rate(self):
        assert win_rate([1, -1, 1, 1]) == 0.75

    def test_win_rate_empty(self):
        assert win_rate([]) == 0

class TestPnL:
    def test_long_profit(self):
        r = calculate_trade_pnl(100, 110, 1, "long")
        assert r["net"] > 0

    def test_long_loss(self):
        r = calculate_trade_pnl(100, 90, 1, "long")
        assert r["net"] < 0

    def test_fees_deducted(self):
        r = calculate_trade_pnl(100, 110, 1)
        assert r["fees"] > 0
        assert r["net"] < r["gross"]
