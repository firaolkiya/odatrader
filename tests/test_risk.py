import pytest
from backend.risk.exposure import check_exposure
from backend.risk.var_calculator import historical_var, parametric_var
from backend.risk.position_sizer import fixed_fraction, kelly_criterion

class TestExposure:
    def test_within_limits(self):
        r = check_exposure({"BTC": 0.1, "ETH": 0.1})
        assert r["ok"]

    def test_exceeds_per_symbol(self):
        r = check_exposure({"BTC": 0.5}, max_per_symbol=0.3)
        assert not r["ok"]

    def test_exceeds_total(self):
        r = check_exposure({"A": 0.6, "B": 0.6}, max_total=1.0)
        assert not r["ok"]

class TestVaR:
    def test_historical_var(self):
        returns = [-0.02, -0.01, 0.01, 0.02, -0.03, 0.01]
        v = historical_var(returns)
        assert v >= 0

    def test_parametric_var(self):
        returns = [-0.02, -0.01, 0.01, 0.02, -0.03]
        v = parametric_var(returns)
        assert v >= 0

    def test_empty_returns(self):
        assert historical_var([]) == 0

class TestPositionSizer:
    def test_fixed_fraction(self):
        size = fixed_fraction(10000, 0.01, 100)
        assert size == 1.0

    def test_fixed_fraction_zero_stop(self):
        assert fixed_fraction(10000, 0.01, 0) == 0

    def test_kelly_positive(self):
        k = kelly_criterion(0.6, 2, 1)
        assert k > 0

    def test_kelly_zero_loss(self):
        assert kelly_criterion(0.6, 2, 0) == 0
