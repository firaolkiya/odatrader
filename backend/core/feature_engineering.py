# backend/core/feature_engineering.py

import pandas as pd
import ta.momentum
import ta.trend
import ta.volatility

def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute technical indicators (momentum, trend, volatility) from OHLCV DataFrame.
    Returns a DataFrame with added features.
    """

    try:
        df.sort_values('timestamp', inplace=True)
        df.reset_index(drop=True, inplace=True)

        # Momentum
        df["rsi"] = ta.momentum.RSIIndicator(close=df["close"], window=14).rsi()

        # Trend
        df["ema_fast"] = ta.trend.EMAIndicator(close=df["close"], window=9).ema_indicator()
        df["ema_slow"] = ta.trend.EMAIndicator(close=df["close"], window=21).ema_indicator()
        df["ema_9"] = df["ema_fast"]
        df["ema_21"] = df["ema_slow"]

        macd = ta.trend.MACD(close=df["close"], window_fast=22, window_slow=26, window_sign=9)
        df["macd"] = macd.macd()
        df["macd_signal"] = macd.macd_signal()

        adx_ind = ta.trend.ADXIndicator(high=df["high"], low=df["low"], close=df["close"], window=14)
        df["adx"] = adx_ind.adx()
        df["plus_di"] = adx_ind.adx_pos()
        df["minus_di"] = adx_ind.adx_neg()

        # Volatility
        bb = ta.volatility.BollingerBands(close=df["close"], window=20)
        df["bb_upper"] = bb.bollinger_hband()
        df["bb_lower"] = bb.bollinger_lband()

        df["donchian_upper"] = df["high"].rolling(20).max()
        df["donchian_lower"] = df["low"].rolling(20).min()

        from backend.strategies.supertrend_strategy import SupertrendStrategy
        df = SupertrendStrategy.compute(df)

        df["vwap"] = (df["close"] * df["volume"]).cumsum() / df["volume"].cumsum()
        df["zscore"] = (df["close"] - df["close"].rolling(20).mean()) / df["close"].rolling(20).std()
        df["roc"] = df["close"].pct_change(10) * 100
        df["stoch_k"] = ta.momentum.StochasticOscillator(
            high=df["high"], low=df["low"], close=df["close"]
        ).stoch()

        # Custom
        df["price_change"] = df["close"].pct_change() * 100
        df["volume_change"] = df["volume"].pct_change()

        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)

        return df

    except Exception as e:
        print(f"[compute_features] ❌ Error: {e}")
        return pd.DataFrame()
