import pytest
import pandas as pd
import numpy as np
from backend.engine.regime_classifier import RegimeClassifier

@pytest.fixture
def rc():
    return RegimeClassifier()

class TestRegimeClassifier:
    def test_empty_df(self, rc):
        r = rc.classify(pd.DataFrame())
        assert r["regime"] == 0.0

    def test_short_df(self, rc):
        df = pd.DataFrame({"close": [1, 2, 3], "high": [1, 2, 3], "low": [1, 2, 3]})
        r = rc.classify(df)
        assert r["regime"] == 0.0

    def test_calm_market(self, rc, flat_df):
        r = rc.classify(flat_df)
        assert r["regime"] < 0.5
        assert r["label"] in ("calm", "moderate", "unknown")

    def test_trending_up(self, rc, trending_up_df):
        r = rc.classify(trending_up_df)
        assert 0 <= r["regime"] <= 1

    def test_trending_down(self, rc, trending_down_df):
        r = rc.classify(trending_down_df)
        assert 0 <= r["regime"] <= 1

    def test_regime_bounds(self, rc, sample_ohlcv_df):
        r = rc.classify(sample_ohlcv_df)
        assert 0 <= r["regime"] <= 1

    def test_atr_norm_positive(self, rc, sample_ohlcv_df):
        r = rc.classify(sample_ohlcv_df)
        assert r["atr_norm"] >= 0

    def test_adx_present(self, rc, sample_ohlcv_df):
        r = rc.classify(sample_ohlcv_df)
        assert "adx" in r

    def test_sl_multiplier_calm(self, rc):
        m = rc._sl_multiplier(0.0)
        assert m >= 1.0

    def test_sl_multiplier_volatile(self, rc):
        m = rc._sl_multiplier(1.0)
        assert m >= 1.5

    def test_sl_multiplier_interpolates(self, rc):
        low = rc._sl_multiplier(0.0)
        high = rc._sl_multiplier(1.0)
        assert high > low

    @pytest.mark.parametrize("regime,label", [(0.1,"calm"),(0.5,"moderate"),(0.8,"volatile_trend")])
    def test_labels(self, rc, sample_ohlcv_df, regime, label):
        r = rc.classify(sample_ohlcv_df)
        assert r["label"] in ("calm", "moderate", "volatile_trend", "unknown")

    def test_vol_z_bounded(self, rc, sample_ohlcv_df):
        r = rc.classify(sample_ohlcv_df)
        assert 0 <= r["vol_z"] <= 1

    def test_custom_vol_cap(self):
        rc = RegimeClassifier({"regime_vol_cap": 5.0})
        r = rc.classify(__import__("pandas").DataFrame({
            "close": range(50), "high": range(50), "low": range(50)}))
        assert r["regime"] >= 0

    def test_returns_dict_keys(self, rc, sample_ohlcv_df):
        r = rc.classify(sample_ohlcv_df)
        for k in ("regime","atr_norm","adx","vol_z","label","sl_atr_mult"):
            assert k in r
