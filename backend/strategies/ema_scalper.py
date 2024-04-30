"""1-minute EMA scalper strategy for fast markets."""
import time
from backend.strategies.base_strategy import BaseStrategy


class EMAScalperStrategy(BaseStrategy):
    """
    Entry: EMA(9) crosses above EMA(21) and RSI < 70
    Exit: profit target 0.25%, trailing 0.15%, or 30s timeout
    Stop: 0.3% below entry
    """

    def __init__(self, profit_target_pct: float = 0.0025, stop_pct: float = 0.003,
                 trail_pct: float = 0.0015, timeout_sec: int = 30):
        super().__init__(name="EMAScalper")
        self.profit_target_pct = profit_target_pct
        self.stop_pct = stop_pct
        self.trail_pct = trail_pct
        self.timeout_sec = timeout_sec
        self._entry_time = None
        self._entry_price = None
        self._trail_high = None

    def evaluate(self, current, previous=None):
        ema9 = current.get("ema_9", current.get("close", 0))
        ema21 = current.get("ema_21", current.get("close", 0))
        rsi = current.get("rsi", 50)
        price = current.get("close", 0)
        prev_ema9 = previous.get("ema_9", ema9) if previous is not None else ema9
        prev_ema21 = previous.get("ema_21", ema21) if previous is not None else ema21

        if self._entry_price:
            pnl_pct = (price - self._entry_price) / self._entry_price
            if pnl_pct >= self.profit_target_pct:
                self._reset()
                return {"action": "SELL", "reason": f"Profit target {pnl_pct:.2%}"}
            if pnl_pct <= -self.stop_pct:
                self._reset()
                return {"action": "SELL", "reason": f"Stop loss {pnl_pct:.2%}"}
            self._trail_high = max(self._trail_high or price, price)
            if price < self._trail_high * (1 - self.trail_pct):
                self._reset()
                return {"action": "SELL", "reason": "Trailing stop hit"}
            if self._entry_time and time.time() - self._entry_time > self.timeout_sec:
                self._reset()
                return {"action": "SELL", "reason": "Timeout exit"}

        if prev_ema9 <= prev_ema21 and ema9 > ema21 and rsi < 70:
            self._entry_price = price
            self._entry_time = time.time()
            self._trail_high = price
            return {"action": "BUY", "reason": f"EMA9/21 cross, RSI={rsi:.1f}"}
        return {"action": "HOLD", "reason": "No scalper signal"}

    def _reset(self):
        self._entry_price = None
        self._entry_time = None
        self._trail_high = None
