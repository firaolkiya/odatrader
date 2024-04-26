"""Alpaca gateway for US equities (AAPL, TSLA)."""
import logging
import httpx
from backend.gateway.base import MarketDataConnector, BrokerConnector
from backend.core.instruments import Instrument
from backend.core.signals import Quote, Bar
from backend.orders.models import Order, OrderStatus

logger = logging.getLogger("odatrade.gateway.alpaca")


class AlpacaGateway(MarketDataConnector, BrokerConnector):
    BASE_URL = "https://paper-api.alpaca.markets"
    DATA_URL = "https://data.alpaca.markets"

    def __init__(self, api_key: str = "", secret: str = "", paper: bool = True):
        self.api_key = api_key
        self.secret = secret
        self.paper = paper
        self._connected = False

    def _headers(self):
        return {"APCA-API-KEY-ID": self.api_key, "APCA-API-SECRET-KEY": self.secret}

    async def connect(self):
        self._connected = bool(self.api_key)
        logger.info("Alpaca gateway %s", "connected" if self._connected else "stub mode")

    async def disconnect(self):
        self._connected = False

    async def subscribe_trades(self, instrument: Instrument, callback):
        logger.info("Alpaca trade stream stub for %s", instrument.symbol)

    async def subscribe_quotes(self, instrument: Instrument, callback):
        try:
            resp = httpx.get(f"{self.DATA_URL}/v2/stocks/{instrument.symbol}/quotes/latest",
                             headers=self._headers(), timeout=5)
            if resp.status_code == 200:
                q = resp.json().get("quote", {})
                from backend.core.signals import Quote
                callback(Quote(ts=0, bid=q.get("bp", 0), ask=q.get("ap", 0),
                               bidsz=q.get("bs", 0), asksz=q.get("as", 0), instrument=instrument.symbol))
        except Exception as e:
            logger.warning("Alpaca quote fetch: %s", e)

    async def subscribe_bars(self, instrument: Instrument, timeframe: str, callback):
        logger.info("Alpaca bar stream stub for %s %s", instrument.symbol, timeframe)

    async def place_order(self, order: Order) -> dict:
        if not self._connected:
            order.status = OrderStatus.FILLED
            return {"status": "paper_filled", "order": order, "mode": "paper"}
        try:
            resp = httpx.post(f"{self.BASE_URL}/v2/orders", headers=self._headers(), json={
                "symbol": order.symbol, "qty": order.quantity,
                "side": order.side.value, "type": "market", "time_in_force": "day",
            }, timeout=10)
            return resp.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def cancel_order(self, clid: str) -> bool:
        return True

    async def get_positions(self) -> list:
        try:
            resp = httpx.get(f"{self.BASE_URL}/v2/positions", headers=self._headers(), timeout=5)
            return resp.json() if resp.status_code == 200 else []
        except Exception:
            return []

    async def get_balance(self) -> dict:
        try:
            resp = httpx.get(f"{self.BASE_URL}/v2/account", headers=self._headers(), timeout=5)
            if resp.status_code == 200:
                acct = resp.json()
                return {"cash": float(acct.get("cash", 0)), "equity": float(acct.get("equity", 0))}
        except Exception:
            pass
        return {"cash": 10000.0, "equity": 10000.0}

    async def get_open_orders(self, symbol: str = None) -> list:
        return []
