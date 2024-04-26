"""Gateway connector interfaces for multi-asset market data and order routing."""
from abc import ABC, abstractmethod
from typing import AsyncIterator, Callable, List, Optional
from backend.core.signals import Quote, Bar
from backend.core.instruments import Instrument
from backend.orders.models import Order


class MarketDataConnector(ABC):
    @abstractmethod
    async def subscribe_trades(self, instrument: Instrument, callback: Callable):
        pass

    @abstractmethod
    async def subscribe_quotes(self, instrument: Instrument, callback: Callable):
        pass

    @abstractmethod
    async def subscribe_bars(self, instrument: Instrument, timeframe: str, callback: Callable):
        pass

    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def disconnect(self):
        pass


class BrokerConnector(ABC):
    @abstractmethod
    async def place_order(self, order: Order) -> dict:
        pass

    @abstractmethod
    async def cancel_order(self, clid: str) -> bool:
        pass

    @abstractmethod
    async def get_positions(self) -> list:
        pass

    @abstractmethod
    async def get_balance(self) -> dict:
        pass

    @abstractmethod
    async def get_open_orders(self, symbol: str = None) -> list:
        pass
