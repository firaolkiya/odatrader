"""OANDA gateway for FX pairs (EURUSD, USDJPY, GBPUSD)."""
import logging
import httpx
from backend.gateway.base import MarketDataConnector, BrokerConnector
from backend.core.instruments import Instrument
from backend.orders.models import Order, OrderStatus

logger = logging.getLogger("odatrade.gateway.oanda")


class OANDAGateway(MarketDataConnector, BrokerConnector):
    BASE_URL = "https://api-fxpractice.oanda.com/v3"

    def __init__(self, api_key: str = "", account_id: str = "", paper: bool = True):
        self.api_key = api_key
        self.account_id = account_id
        self.paper = paper
        self._connected = False

    def _headers(self):
        return {"Authorization": f"Bearer {self.api_key}"}

    async def connect(self):
        self._connected = bool(self.api_key)
        logger.info("OANDA gateway %s", "connected" if self._connected else "stub mode")

    async def disconnect(self):
        self._connected = False

    async def subscribe_trades(self, instrument: Instrument, callback):
        pass

    async def subscribe_quotes(self, instrument: Instrument, callback):
        try:
            resp = httpx.get(f"{self.BASE_URL}/accounts/{self.account_id}/pricing",
                             headers=self._headers(),
                             params={"instruments": instrument.symbol}, timeout=5)
            if resp.status_code == 200:
                prices = resp.json().get("prices", [{}])[0]
                from backend.core.signals import Quote
                bids = prices.get("bids", [{}])
                asks = prices.get("asks", [{}])
                callback(Quote(ts=0, bid=float(bids[0].get("price", 0)),
                               ask=float(asks[0].get("price", 0)), instrument=instrument.symbol))
        except Exception as e:
            logger.warning("OANDA quote: %s", e)

    async def subscribe_bars(self, instrument: Instrument, timeframe: str, callback):
        pass

    async def place_order(self, order: Order) -> dict:
        if not self._connected:
            order.status = OrderStatus.FILLED
            return {"status": "paper_filled", "mode": "paper"}
        try:
            resp = httpx.post(f"{self.BASE_URL}/accounts/{self.account_id}/orders",
                              headers=self._headers(), json={
                                  "order": {"instrument": instrument_symbol(order.symbol),
                                            "units": str(int(order.quantity)), "type": "MARKET",
                                            "side": order.side.value.upper()}}, timeout=10)
            return resp.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def cancel_order(self, clid: str) -> bool:
        return True

    async def get_positions(self) -> list:
        return []

    async def get_balance(self) -> dict:
        return {"USD": 10000.0}

    async def get_open_orders(self, symbol: str = None) -> list:
        return []


def instrument_symbol(symbol: str) -> str:
    if len(symbol) == 6:
        return f"{symbol[:3]}_{symbol[3:]}"
    return symbol
