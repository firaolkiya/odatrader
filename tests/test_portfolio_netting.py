import pytest
from backend.risk.portfolio_netting import check_portfolio_limits, correlated_exposure, net_positions


class TestPortfolioNetting:
    def test_net_positions(self):
        n = net_positions({"btc": (1.0, 50000), "eth": (-2.0, 3000)})
        assert n["btc"] == 50000
        assert n["eth"] == -6000

    def test_uncorrelated_exposure(self):
        exp = correlated_exposure({"btc": 0.5, "eth": 0.5}, {})
        assert exp > 0.7

    def test_high_correlation_increases_exposure(self):
        corr = {"btc": {"eth": 0.9}, "eth": {"btc": 0.9}}
        low = correlated_exposure({"btc": 0.3, "eth": 0.3}, {"btc": {"eth": 0.0}})
        high = correlated_exposure({"btc": 0.3, "eth": 0.3}, corr)
        assert high >= low

    def test_violation_on_correlated_cap(self):
        r = check_portfolio_limits(
            {"btc": 0.8, "eth": 0.8},
            {"btc": {"eth": 0.95}, "eth": {"btc": 0.95}},
            max_per_symbol=1.0,
            max_correlated_total=0.5,
        )
        assert not r["ok"]
