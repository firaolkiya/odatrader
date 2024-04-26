"""Supertrend indicator strategy."""
from backend.strategies.base_strategy import BaseStrategy
import pandas as pd


class SupertrendStrategy(BaseStrategy):
    def __init__(self, period: int = 10, multiplier: float = 3.0):
        super().__init__(name="Supertrend")
        self.period = period
        self.multiplier = multiplier

    def evaluate(self, current, previous=None):
        st = current.get("supertrend", current.get("close", 0))
        price = current.get("close", 0)
        prev_st = previous.get("supertrend", st) if previous is not None else st
        if price > st and (previous is None or previous.get("close", 0) <= prev_st):
            return {"action": "BUY", "reason": f"Supertrend bullish cross @ {st:.2f}"}
        if price < st and (previous is None or previous.get("close", 0) >= prev_st):
            return {"action": "SELL", "reason": f"Supertrend bearish cross @ {st:.2f}"}
        return {"action": "HOLD", "reason": "Supertrend neutral"}

    @staticmethod
    def compute(df: pd.DataFrame, period: int = 10, multiplier: float = 3.0) -> pd.DataFrame:
        hl2 = (df["high"] + df["low"]) / 2
        atr = (df["high"] - df["low"]).rolling(period).mean()
        upper = hl2 + multiplier * atr
        lower = hl2 - multiplier * atr
        st = pd.Series(0.0, index=df.index)
        for i in range(1, len(df)):
            if df["close"].iloc[i] > upper.iloc[i - 1]:
                st.iloc[i] = lower.iloc[i]
            elif df["close"].iloc[i] < lower.iloc[i - 1]:
                st.iloc[i] = upper.iloc[i]
            else:
                st.iloc[i] = st.iloc[i - 1]
        df["supertrend"] = st
        return df
