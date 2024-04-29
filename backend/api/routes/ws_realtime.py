"""WebSocket hub for real-time PnL, trades, and signal updates."""
import asyncio
import json
import logging
from typing import Dict, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

logger = logging.getLogger("odatrade.ws")


class ConnectionManager:
    """Manages WebSocket connections per channel."""

    def __init__(self):
        self._connections: Dict[str, Set[WebSocket]] = {
            "pnl": set(),
            "trades": set(),
            "signals": set(),
            "bots": set(),
            "all": set(),
        }

    async def connect(self, channel: str, websocket: WebSocket):
        await websocket.accept()
        if channel not in self._connections:
            self._connections[channel] = set()
        self._connections[channel].add(websocket)
        self._connections["all"].add(websocket)
        logger.info("WS connected: channel=%s, total=%d", channel, len(self._connections[channel]))

    def disconnect(self, channel: str, websocket: WebSocket):
        self._connections.get(channel, set()).discard(websocket)
        self._connections["all"].discard(websocket)

    async def broadcast(self, channel: str, data: dict):
        message = json.dumps(data, default=str)
        targets = self._connections.get(channel, set()) | self._connections.get("all", set())
        dead = set()
        for ws in targets:
            try:
                await ws.send_text(message)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self.disconnect(channel, ws)

    @property
    def connection_count(self) -> int:
        return len(self._connections["all"])


manager = ConnectionManager()
router = APIRouter(tags=["websocket-realtime"])


@router.websocket("/ws/realtime")
async def realtime_all(websocket: WebSocket):
    await manager.connect("all", websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({"type": "ack", "received": data})
    except WebSocketDisconnect:
        manager.disconnect("all", websocket)


@router.websocket("/ws/pnl/{bot_id}")
async def pnl_stream(websocket: WebSocket, bot_id: str):
    await manager.connect("pnl", websocket)
    try:
        await websocket.send_json({"type": "pnl_subscribed", "bot_id": bot_id})
        while True:
            await asyncio.sleep(30)
            await websocket.send_json({"type": "pnl_heartbeat", "bot_id": bot_id})
    except WebSocketDisconnect:
        manager.disconnect("pnl", websocket)


@router.websocket("/ws/trades/{bot_id}")
async def trades_stream(websocket: WebSocket, bot_id: str):
    await manager.connect("trades", websocket)
    try:
        await websocket.send_json({"type": "trades_subscribed", "bot_id": bot_id})
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect("trades", websocket)


@router.websocket("/ws/signals/{bot_id}")
async def signals_stream(websocket: WebSocket, bot_id: str):
    await manager.connect("signals", websocket)
    try:
        await websocket.send_json({"type": "signals_subscribed", "bot_id": bot_id})
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect("signals", websocket)


@router.websocket("/ws/bots")
async def bots_stream(websocket: WebSocket):
    await manager.connect("bots", websocket)
    try:
        await websocket.send_json({"type": "bots_subscribed"})
        while True:
            await asyncio.sleep(10)
            await websocket.send_json({"type": "bots_heartbeat"})
    except WebSocketDisconnect:
        manager.disconnect("bots", websocket)


async def broadcast_pnl(bot_id: str, pnl_data: dict):
    await manager.broadcast("pnl", {"type": "pnl_update", "bot_id": bot_id, **pnl_data})


async def broadcast_trade(bot_id: str, trade_data: dict):
    await manager.broadcast("trades", {"type": "trade", "bot_id": bot_id, **trade_data})


async def broadcast_signal(bot_id: str, signal_data: dict):
    await manager.broadcast("signals", {"type": "signal", "bot_id": bot_id, **signal_data})
