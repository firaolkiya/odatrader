"""Simulated limit order book."""
from typing import List, Tuple

class OrderBook:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.bids: List[Tuple[float, float]] = []
        self.asks: List[Tuple[float, float]] = []

    def add_bid(self, price: float, qty: float):
        self.bids.append((price, qty))
        self.bids.sort(key=lambda x: -x[0])

    def add_ask(self, price: float, qty: float):
        self.asks.append((price, qty))
        self.asks.sort(key=lambda x: x[0])

    def best_bid(self):
        return self.bids[0] if self.bids else None

    def best_ask(self):
        return self.asks[0] if self.asks else None

    def spread(self):
        bb, ba = self.best_bid(), self.best_ask()
        if bb and ba:
            return ba[0] - bb[0]
        return None
