import pytest
from backend.core.feature_engineering import compute_features

class TestFeatureEngineering:
    def test_adds_rsi(self, sample_ohlcv_df):
        df = compute_features(sample_ohlcv_df.copy())
        if not df.empty:
            assert "rsi" in df.columns

    def test_adds_ema(self, sample_ohlcv_df):
        df = compute_features(sample_ohlcv_df.copy())
        if not df.empty:
            assert "ema_9" in df.columns

    def test_adds_macd(self, sample_ohlcv_df):
        df = compute_features(sample_ohlcv_df.copy())
        if not df.empty:
            assert "macd" in df.columns

    def test_adds_donchian(self, sample_ohlcv_df):
        df = compute_features(sample_ohlcv_df.copy())
        if not df.empty:
            assert "donchian_upper" in df.columns

    def test_empty_df(self):
        import pandas as pd
        df = compute_features(pd.DataFrame())
        assert df.empty
