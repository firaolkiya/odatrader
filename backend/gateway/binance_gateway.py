"""Binance gateway: spot + perp WebSocket market data."""
import logging
import asyncio
from typing import Callable, List
from backend.gateway.base import MarketDataConnector, BrokerConnector
from backend.core.instruments import Instrument
from backend.core.signals import Quote, Bar
from backend.orders.models import Order, OrderSide, OrderStatus

logger = logging.getLogger("odatrade.gateway.binance")


class BinanceGateway(MarketDataConnector, BrokerConnector):
    def __init__(self, api_key: str = "", secret: str = ""):
        self.api_key = api_key
        self.secret = secret
        self._ws_manager = None
        self._connected = False
        self._callbacks = {"trades": [], "quotes": [], "bars": []}

    async def connect(self):
        try:
            from binance import ThreadedWebsocketManager
            self._ws_manager = ThreadedWebsocketManager(api_key=self.api_key, api_secret=self.secret)
            self._ws_manager.start()
            self._connected = True
            logger.info("Binance gateway connected")
        except Exception as e:
            logger.error("Binance connect failed: %s", e)

    async def disconnect(self):
        if self._ws_manager:
            self._ws_manager.stop()
        self._connected = False

    async def subscribe_trades(self, instrument: Instrument, callback: Callable):
        if not self._ws_manager:
            return
        sym = instrument.symbol.replace("-PERP", "").upper()

        def on_msg(msg):
            if msg.get("e") == "trade":
                callback({"ts": msg["T"] / 1000, "price": float(msg["p"]),
                          "size": float(msg["q"]), "side": "B" if msg["m"] else "S", "instrument": instrument.symbol})

        self._ws_manager.start_trade_socket(callback=on_msg, symbol=sym)

    async def subscribe_quotes(self, instrument: Instrument, callback: Callable):
        sym = instrument.symbol.replace("-PERP", "").upper()

        def on_msg(msg):
            if msg.get("e") == "bookTicker":
                callback(Quote(ts=msg.get("E", 0) / 1000, bid=float(msg["b"]), ask=float(msg["a"]),
                               bidsz=float(msg["B"]), asksz=float(msg["A"]), instrument=instrument.symbol))

        if self._ws_manager:
            self._ws_manager.start_symbol_book_ticker_socket(callback=on_msg, symbol=sym)

    async def subscribe_bars(self, instrument: Instrument, timeframe: str, callback: Callable):
        sym = instrument.symbol.replace("-PERP", "").upper()

        def on_msg(msg):
            if msg.get("e") == "kline" and msg["k"]["x"]:
                k = msg["k"]
                callback(Bar(ts=k["t"] / 1000, o=float(k["o"]), h=float(k["h"]), l=float(k["l"]),
                             c=float(k["c"]), v=float(k["v"]), timeframe=timeframe, instrument=instrument.symbol))

        if self._ws_manager:
            self._ws_manager.start_kline_socket(callback=on_msg, symbol=sym, interval=timeframe)

    async def place_order(self, order: Order) -> dict:
        try:
            from backend.exchange.binance import BinanceExchange
            ex = BinanceExchange(self.api_key, self.secret)
            side = "buy" if order.side == OrderSide.BUY else "sell"
            result = ex.create_order(order.symbol, side, order.quantity, order_type=order.price and "limit" or "market")
            order.status = OrderStatus.FILLED
            return {"status": "filled", "exchange_id": result.get("id"), "order": order}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def cancel_order(self, clid: str) -> bool:
        return True

    async def get_positions(self) -> list:
        return []

    async def get_balance(self) -> dict:
        try:
            from backend.exchange.binance import BinanceExchange
            ex = BinanceExchange(self.api_key, self.secret)
            return {"USDT": ex.get_balance("USDT")}
        except Exception:
            return {}

    async def get_open_orders(self, symbol: str = None) -> list:
        return []
