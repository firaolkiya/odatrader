import pytest
import pandas as pd
import numpy as np
from backend.ml.model_registry import ModelRegistry
from backend.ml.feature_pipeline import add_lag_features, add_rolling_stats

class TestModelRegistry:
    def test_register(self):
        ModelRegistry.register("test_model", "/path/model.pkl", "v1", {"rmse": 0.01})
        assert ModelRegistry.get("test_model") is not None

    def test_list(self):
        ModelRegistry.register("m2", "/p", "v2")
        assert "m2" in ModelRegistry.list_models()

class TestFeaturePipeline:
    def test_lag_features(self, sample_ohlcv_df):
        df = add_lag_features(sample_ohlcv_df.copy(), ["close"], lags=[1])
        assert "close_lag_1" in df.columns

    def test_rolling_stats(self, sample_ohlcv_df):
        df = add_rolling_stats(sample_ohlcv_df.copy(), "close", windows=[5])
        assert "close_mean_5" in df.columns
