"""Volatility regime detection."""
import pandas as pd

def atr_percentile(df: pd.DataFrame, window: int = 14) -> float:
    if len(df) < window:
        return 0.0
    tr = (df["high"] - df["low"]).rolling(window).mean()
    return float(tr.iloc[-1] / df["close"].iloc[-1] * 100)

def is_high_volatility(df: pd.DataFrame, threshold: float = 2.0) -> bool:
    return atr_percentile(df) > threshold
