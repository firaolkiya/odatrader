"""Extended ML feature pipeline."""
import pandas as pd
import numpy as np

def add_lag_features(df: pd.DataFrame, cols: list, lags: list = [1, 3, 5]) -> pd.DataFrame:
    for col in cols:
        for lag in lags:
            df[f"{col}_lag_{lag}"] = df[col].shift(lag)
    return df.dropna()

def add_rolling_stats(df: pd.DataFrame, col: str, windows: list = [5, 10, 20]) -> pd.DataFrame:
    for w in windows:
        df[f"{col}_mean_{w}"] = df[col].rolling(w).mean()
        df[f"{col}_std_{w}"] = df[col].rolling(w).std()
    return df.dropna()
