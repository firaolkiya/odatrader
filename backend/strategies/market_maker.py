"""Passive market-making strategy."""
from backend.strategies.base_strategy import BaseStrategy


class MarketMakerStrategy(BaseStrategy):
    """
    Place symmetric limit buy at mid - spread/2 and sell at mid + spread/2.
    Inventory skew when net inventory exceeds threshold.
    """

    def __init__(self, spread_pct: float = 0.001, inventory_threshold: float = 0.1):
        super().__init__(name="MarketMaker")
        self.spread_pct = spread_pct
        self.inventory_threshold = inventory_threshold
        self._inventory = 0.0

    def evaluate(self, current, previous=None):
        bid = current.get("bid", current.get("close", 0) * (1 - self.spread_pct / 2))
        ask = current.get("ask", current.get("close", 0) * (1 + self.spread_pct / 2))
        mid = (bid + ask) / 2
        spread = ask - bid

        buy_px = mid - spread / 2
        sell_px = mid + spread / 2

        if self._inventory > self.inventory_threshold:
            return {"action": "SELL", "reason": f"Inventory skew sell @ {sell_px:.4f} (inv={self._inventory:.3f})",
                    "order_type": "limit", "price": sell_px, "post_only": True}
        if self._inventory < -self.inventory_threshold:
            return {"action": "BUY", "reason": f"Inventory skew buy @ {buy_px:.4f} (inv={self._inventory:.3f})",
                    "order_type": "limit", "price": buy_px, "post_only": True}

        if current.get("close", 0) <= buy_px:
            self._inventory += 1
            return {"action": "BUY", "reason": f"MM bid fill @ {buy_px:.4f}",
                    "order_type": "limit", "price": buy_px, "post_only": True}
        if current.get("close", 0) >= sell_px:
            self._inventory -= 1
            return {"action": "SELL", "reason": f"MM ask fill @ {sell_px:.4f}",
                    "order_type": "limit", "price": sell_px, "post_only": True}
        return {"action": "HOLD", "reason": "MM quoting", "bid": buy_px, "ask": sell_px}
