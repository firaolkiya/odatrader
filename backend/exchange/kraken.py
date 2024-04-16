"""Kraken exchange adapter stub."""
from backend.exchange.base import BaseExchange

class KrakenExchange(BaseExchange):
    def __init__(self, api_key: str = "", secret: str = ""):
        self.api_key = api_key
        self.secret = secret

    def get_ohlcv(self, symbol: str, timeframe: str = "1m", limit: int = 100):
        raise NotImplementedError("Kraken adapter stub")

    def create_order(self, symbol: str, side: str, amount: float, order_type: str = "market"):
        raise NotImplementedError("Kraken adapter stub")

    def get_balance(self, asset: str):
        return 0.0

    def get_open_orders(self, symbol: str):
        return []
