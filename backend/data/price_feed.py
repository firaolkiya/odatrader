"""Unified price feed aggregator."""
from typing import Dict
from odatrade.core.cache import TTLCache

class PriceFeed:
    def __init__(self):
        self.cache = TTLCache(default_ttl=5)
        self.prices: Dict[str, float] = {}

    def update(self, symbol: str, price: float):
        self.prices[symbol] = price
        self.cache.set(symbol, price)

    def get(self, symbol: str):
        return self.cache.get(symbol) or self.prices.get(symbol)

    def get_all(self):
        return dict(self.prices)
