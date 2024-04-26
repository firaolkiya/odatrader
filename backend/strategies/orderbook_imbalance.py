"""Orderbook imbalance sniffer strategy."""
from backend.strategies.base_strategy import BaseStrategy


class OrderbookImbalanceStrategy(BaseStrategy):
    """
    Metric: (bid_volume - ask_volume) / total_volume
    Fire trade when imbalance > threshold and price sweep occurs.
    """

    def __init__(self, threshold: float = 0.3, top_n: int = 5):
        super().__init__(name="OrderbookImbalance")
        self.threshold = threshold
        self.top_n = top_n

    def evaluate(self, current, previous=None, imbalance: float = None):
        if imbalance is not None:
            imb = imbalance
        else:
            bid_vol = current.get("bid_volume", current.get("bidsz", 0))
            ask_vol = current.get("ask_volume", current.get("asksz", 0))
            total = bid_vol + ask_vol
            imb = (bid_vol - ask_vol) / total if total > 0 else 0

        price_change = 0
        if previous is not None:
            price_change = current.get("close", 0) - previous.get("close", 0)

        if imb > self.threshold and price_change > 0:
            return {"action": "BUY", "reason": f"OB imbalance {imb:.2f} + price sweep up"}
        if imb < -self.threshold and price_change < 0:
            return {"action": "SELL", "reason": f"OB imbalance {imb:.2f} + price sweep down"}
        return {"action": "HOLD", "reason": f"OB imbalance {imb:.2f}"}

    @staticmethod
    def compute_imbalance(bids: list, asks: list, top_n: int = 5) -> float:
        bid_vol = sum(q for _, q in bids[:top_n])
        ask_vol = sum(q for _, q in asks[:top_n])
        total = bid_vol + ask_vol
        return (bid_vol - ask_vol) / total if total > 0 else 0.0
