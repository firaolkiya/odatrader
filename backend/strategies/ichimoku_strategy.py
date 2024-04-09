"""IchimokuStrategy strategy for OdaTrade."""
from backend.strategies.base_strategy import BaseStrategy

class IchimokuStrategy(BaseStrategy):
    def evaluate(self, current, previous=None):
        
        price = current.get("close", 0)
        span_a = current.get("ichimoku_a", price)
        span_b = current.get("ichimoku_b", price)
        if price > max(span_a, span_b): return {"action": "BUY", "reason": "Above cloud"}
        if price < min(span_a, span_b): return {"action": "SELL", "reason": "Below cloud"}
        return {"action": "HOLD", "reason": "Inside cloud"}
