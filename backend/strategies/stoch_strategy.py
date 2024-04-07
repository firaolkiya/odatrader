"""StochasticStrategy strategy for OdaTrade."""
from backend.strategies.base_strategy import BaseStrategy

class StochasticStrategy(BaseStrategy):
    def evaluate(self, current, previous=None):
        
        k = current.get("stoch_k", 50)
        if k < 20: return {"action": "BUY", "reason": f"Stoch oversold {k:.1f}"}
        if k > 80: return {"action": "SELL", "reason": f"Stoch overbought {k:.1f}"}
        return {"action": "HOLD", "reason": "Stoch neutral"}
