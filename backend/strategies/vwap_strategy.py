"""VWAPStrategy strategy for OdaTrade."""
from backend.strategies.base_strategy import BaseStrategy

class VWAPStrategy(BaseStrategy):
    def evaluate(self, current, previous=None):
        
        price = current.get("close", 0)
        vwap = current.get("vwap", price)
        if price < vwap * 0.995: return {"action": "BUY", "reason": "Below VWAP"}
        if price > vwap * 1.005: return {"action": "SELL", "reason": "Above VWAP"}
        return {"action": "HOLD", "reason": "Near VWAP"}
