"""Donchian channel breakout strategy."""
from backend.strategies.base_strategy import BaseStrategy


class DonchianStrategy(BaseStrategy):
    def __init__(self, period: int = 20):
        super().__init__(name="Donchian")
        self.period = period

    def evaluate(self, current, previous=None):
        price = current.get("close", 0)
        upper = current.get("donchian_upper", price)
        lower = current.get("donchian_lower", price)
        if price >= upper:
            return {"action": "BUY", "reason": f"Donchian breakout above {upper:.2f}"}
        if price <= lower:
            return {"action": "SELL", "reason": f"Donchian breakdown below {lower:.2f}"}
        return {"action": "HOLD", "reason": "Inside Donchian channel"}
