"""ADXStrategy strategy for OdaTrade."""
from backend.strategies.base_strategy import BaseStrategy

class ADXStrategy(BaseStrategy):
    def evaluate(self, current, previous=None):
        
        adx = current.get("adx", 0)
        plus_di = current.get("plus_di", 0)
        minus_di = current.get("minus_di", 0)
        if adx > 25 and plus_di > minus_di: return {"action": "BUY", "reason": "Strong uptrend"}
        if adx > 25 and minus_di > plus_di: return {"action": "SELL", "reason": "Strong downtrend"}
        return {"action": "HOLD", "reason": "Weak trend"}
