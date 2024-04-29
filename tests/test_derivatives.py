import pytest
from backend.derivatives.leverage import volatility_aware_size, LeverageManager
from backend.derivatives.funding import FundingRateFilter
from backend.derivatives.greeks import black_scholes_greeks

class TestLeverageSizing:
    def test_basic_size(self):
        r = volatility_aware_size(10000, 0.01, 2, 2, 50000)
        assert r["size"] >= 0

    def test_zero_atr(self):
        r = volatility_aware_size(10000, 0.01, 0, 2, 50000)
        assert r["size"] == 0

    @pytest.mark.parametrize("equity,risk", [(10000,0.01),(50000,0.005),(1000,0.02)])
    def test_various_equity(self, equity, risk):
        r = volatility_aware_size(equity, risk, 2, 2, 50000)
        assert r["notional"] >= 0

class TestLeverageManager:
    def test_within_limits(self):
        lm = LeverageManager()
        ok, _ = lm.check_leverage("BTC", 1000, 10000)
        assert ok

    def test_exceeds_per_instrument(self):
        lm = LeverageManager(max_per_instrument=0.05)
        ok, reason = lm.check_leverage("BTC", 10000, 10000)
        assert not ok

class TestFundingFilter:
    def test_allows_normal(self):
        f = FundingRateFilter()
        ok, _ = f.should_trade(0.0001, "long")
        assert ok

    def test_blocks_high_funding_long(self):
        f = FundingRateFilter(max_funding=0.0005)
        ok, _ = f.should_trade(0.01, "long")
        assert not ok

    def test_adjust_pnl(self):
        f = FundingRateFilter()
        adjusted = f.adjust_expected_pnl(100, 0.001, 10000, 8)
        assert adjusted < 100

class TestGreeks:
    def test_call_delta_positive(self):
        g = black_scholes_greeks(100, 100, 0.25, 0.05, 0.2, "call")
        assert g["delta"] > 0

    def test_put_delta_negative(self):
        g = black_scholes_greeks(100, 100, 0.25, 0.05, 0.2, "put")
        assert g["delta"] < 0

    def test_gamma_positive(self):
        g = black_scholes_greeks(100, 100, 0.25, 0.05, 0.2)
        assert g["gamma"] >= 0

    def test_zero_time(self):
        g = black_scholes_greeks(100, 100, 0, 0.05, 0.2)
        assert g["delta"] == 0

    @pytest.mark.parametrize("S,K", [(100,100),(100,90),(100,110),(50,60)])
    def test_various_strikes(self, S, K):
        g = black_scholes_greeks(S, K, 0.5, 0.05, 0.3)
        assert "price" in g
