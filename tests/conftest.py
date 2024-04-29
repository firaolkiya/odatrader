"""Shared pytest fixtures for OdaTrade tests."""
import os
import sys
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def sample_ohlcv_df():
    np.random.seed(42)
    n = 100
    close = 100 + np.cumsum(np.random.randn(n) * 0.5)
    return pd.DataFrame({
        "timestamp": pd.date_range("2025-01-01", periods=n, freq="1min"),
        "open": close + np.random.randn(n) * 0.1,
        "high": close + abs(np.random.randn(n) * 0.3),
        "low": close - abs(np.random.randn(n) * 0.3),
        "close": close,
        "volume": np.random.rand(n) * 1000,
    })


@pytest.fixture
def trending_up_df():
    n = 80
    close = np.linspace(100, 120, n) + np.random.randn(n) * 0.2
    return pd.DataFrame({
        "open": close - 0.1, "high": close + 0.5,
        "low": close - 0.5, "close": close,
        "volume": np.ones(n) * 500,
    })


@pytest.fixture
def trending_down_df():
    n = 80
    close = np.linspace(120, 100, n) + np.random.randn(n) * 0.2
    return pd.DataFrame({
        "open": close + 0.1, "high": close + 0.5,
        "low": close - 0.5, "close": close,
        "volume": np.ones(n) * 500,
    })


@pytest.fixture
def flat_df():
    n = 80
    close = np.ones(n) * 100 + np.random.randn(n) * 0.05
    return pd.DataFrame({
        "open": close, "high": close + 0.1,
        "low": close - 0.1, "close": close,
        "volume": np.ones(n) * 200,
    })


@pytest.fixture
def sample_candle():
    return {"t": 1700000000000, "o": "100", "h": "101", "l": "99", "c": "100.5", "v": "50"}


@pytest.fixture
def auth_token():
    from backend.auth.jwt_handler import create_token
    return create_token("testuser", expires_in=3600)


@pytest.fixture
def api_client():
    from fastapi.testclient import TestClient
    from backend.api.main import app
    return TestClient(app)
