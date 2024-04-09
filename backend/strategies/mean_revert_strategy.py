"""MeanRevertStrategy strategy for OdaTrade."""
from backend.strategies.base_strategy import BaseStrategy

class MeanRevertStrategy(BaseStrategy):
    def evaluate(self, current, previous=None):
        
        z = current.get("zscore", 0)
        if z < -2: return {"action": "BUY", "reason": f"Oversold z={z:.2f}"}
        if z > 2: return {"action": "SELL", "reason": f"Overbought z={z:.2f}"}
        return {"action": "HOLD", "reason": "Normal range"}
