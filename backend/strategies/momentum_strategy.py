"""MomentumStrategy strategy for OdaTrade."""
from backend.strategies.base_strategy import BaseStrategy

class MomentumStrategy(BaseStrategy):
    def evaluate(self, current, previous=None):
        
        roc = current.get("roc", 0)
        if roc > 2: return {"action": "BUY", "reason": f"Momentum up {roc:.2f}%"}
        if roc < -2: return {"action": "SELL", "reason": f"Momentum down {roc:.2f}%"}
        return {"action": "HOLD", "reason": "Flat momentum"}
