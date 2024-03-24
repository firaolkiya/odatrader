# backend/exchange/base.py

from abc import ABC, abstractmethod

class BaseExchange(ABC):
    @abstractmethod
    def get_ohlcv(self, symbol: str, timeframe: str, limit: int = 100):
        pass

    @abstractmethod
    def create_order(self, symbol: str, side: str, amount: float, order_type: str = "market"):
        pass

    @abstractmethod
    def get_balance(self, asset: str):
        pass

    @abstractmethod
    def get_open_orders(self, symbol: str):
        pass

    @abstractmethod
    def cancel_order(self, order_id: str, symbol: str):
        pass
