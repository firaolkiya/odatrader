"""WebSocket streams for quotes and trades."""
import asyncio
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger("odatrade.ws.quotes")


class QuoteTradeManager:
    def __init__(self):
        self.quote_clients: set = set()
        self.trade_clients: set = set()

    async def connect_quotes(self, ws: WebSocket):
        await ws.accept()
        self.quote_clients.add(ws)

    async def connect_trades(self, ws: WebSocket):
        await ws.accept()
        self.trade_clients.add(ws)

    def disconnect(self, ws: WebSocket):
        self.quote_clients.discard(ws)
        self.trade_clients.discard(ws)

    async def broadcast_quote(self, data: dict):
        msg = json.dumps({"type": "quote", **data}, default=str)
        dead = set()
        for ws in self.quote_clients:
            try:
                await ws.send_text(msg)
            except Exception:
                dead.add(ws)
        self.quote_clients -= dead

    async def broadcast_trade(self, data: dict):
        msg = json.dumps({"type": "trade", **data}, default=str)
        dead = set()
        for ws in self.trade_clients:
            try:
                await ws.send_text(msg)
            except Exception:
                dead.add(ws)
        self.trade_clients -= dead


qt_manager = QuoteTradeManager()
router = APIRouter(tags=["ws-quotes-trades"])


@router.websocket("/ws/quotes/{symbol}")
async def quotes_stream(ws: WebSocket, symbol: str):
    await qt_manager.connect_quotes(ws)
    try:
        await ws.send_json({"type": "subscribed", "stream": "quotes", "symbol": symbol})
        while True:
            await asyncio.sleep(1)
            await ws.send_json({"type": "quote_heartbeat", "symbol": symbol})
    except WebSocketDisconnect:
        qt_manager.disconnect(ws)


@router.websocket("/ws/trades/{symbol}")
async def trades_stream(ws: WebSocket, symbol: str):
    await qt_manager.connect_trades(ws)
    try:
        await ws.send_json({"type": "subscribed", "stream": "trades", "symbol": symbol})
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        qt_manager.disconnect(ws)


@router.websocket("/ws/signals")
async def signals_stream(ws: WebSocket):
    await ws.accept()
    try:
        await ws.send_json({"type": "subscribed", "stream": "signals"})
        while True:
            await asyncio.sleep(2)
            await ws.send_json({"type": "signals_heartbeat"})
    except WebSocketDisconnect:
        pass
