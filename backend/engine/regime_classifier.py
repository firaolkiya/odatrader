"""Market regime classifier: trend/volatility/liquidity → regime ∈ [0,1]."""
import math
from typing import Dict, Optional
import pandas as pd
import numpy as np


class RegimeClassifier:
    """
    0 = calm/sideways, 1 = trending/high-vol.
    Uses ATR, ADX, realized vol, spread proxy.
    """

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.vol_cap = self.config.get("regime_vol_cap", 2.0)
        self.adx_trend_threshold = self.config.get("adx_trend_threshold", 25)

    def classify(self, df: pd.DataFrame) -> Dict:
        if df.empty or len(df) < 20:
            return {"regime": 0.0, "atr_norm": 0.0, "adx": 0.0, "vol_z": 0.0, "label": "unknown"}

        close = df["close"].astype(float)
        high = df["high"].astype(float) if "high" in df.columns else close
        low = df["low"].astype(float) if "low" in df.columns else close

        atr = self._atr(high, low, close, 14)
        atr_norm = float(atr.iloc[-1] / close.iloc[-1]) if close.iloc[-1] else 0

        adx = self._adx(high, low, close, 14)
        adx_val = float(adx.iloc[-1]) if not pd.isna(adx.iloc[-1]) else 0

        returns = close.pct_change().dropna()
        vol = float(returns.std() * math.sqrt(252 * 24 * 60)) if len(returns) > 5 else 0
        vol_z = min(1.0, vol / self.vol_cap)

        atr_score = min(1.0, atr_norm / 0.03)
        adx_score = min(1.0, adx_val / 50.0)
        regime = 0.4 * atr_score + 0.4 * adx_score + 0.2 * vol_z
        regime = max(0.0, min(1.0, regime))

        if regime < 0.3:
            label = "calm"
        elif regime < 0.6:
            label = "moderate"
        else:
            label = "volatile_trend"

        return {
            "regime": regime,
            "atr_norm": atr_norm,
            "adx": adx_val,
            "vol_z": vol_z,
            "label": label,
            "sl_atr_mult": self._sl_multiplier(regime),
        }

    def _sl_multiplier(self, regime: float) -> float:
        calm = self.config.get("sl_atr_mult", {}).get("calm", 1.5) if isinstance(self.config.get("sl_atr_mult"), dict) else 1.5
        volatile = self.config.get("sl_atr_mult", {}).get("volatile", 2.8) if isinstance(self.config.get("sl_atr_mult"), dict) else 2.8
        return calm + (volatile - calm) * regime

    @staticmethod
    def _atr(high, low, close, period=14):
        tr = pd.concat([
            high - low,
            (high - close.shift()).abs(),
            (low - close.shift()).abs(),
        ], axis=1).max(axis=1)
        return tr.rolling(period).mean()

    @staticmethod
    def _adx(high, low, close, period=14):
        plus_dm = high.diff()
        minus_dm = -low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        tr = RegimeClassifier._atr(high, low, close, period)
        plus_di = 100 * (plus_dm.rolling(period).mean() / tr)
        minus_di = 100 * (minus_dm.rolling(period).mean() / tr)
        dx = 100 * ((plus_di - minus_di).abs() / (plus_di + minus_di + 1e-10))
        return dx.rolling(period).mean()
