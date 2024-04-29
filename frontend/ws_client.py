"""WebSocket client for real-time OdaTrade dashboard updates."""
import json
import logging
import threading
import time
from typing import Callable, Dict, List, Optional

logger = logging.getLogger("odatrade.frontend.ws")

try:
    import websocket
    WS_AVAILABLE = True
except ImportError:
    WS_AVAILABLE = False


class OdaTradeWebSocketClient:
    """Connects to OdaTrade WebSocket endpoints for live data."""

    def __init__(self, base_url: str = "ws://localhost:8000"):
        self.base_url = base_url.replace("http://", "ws://").replace("https://", "wss://")
        self._connections: Dict[str, object] = {}
        self._callbacks: Dict[str, List[Callable]] = {
            "pnl": [], "trades": [], "signals": [], "bots": [], "all": [],
        }
        self._running = False
        self._threads: Dict[str, threading.Thread] = {}
        self._latest_data: Dict[str, dict] = {}

    def on(self, event_type: str, callback: Callable):
        self._callbacks.setdefault(event_type, []).append(callback)

    def _make_handler(self, channel: str):
        def on_message(ws, message):
            try:
                data = json.loads(message)
                self._latest_data[channel] = data
                for cb in self._callbacks.get(channel, []):
                    cb(data)
                for cb in self._callbacks.get("all", []):
                    cb(data)
            except json.JSONDecodeError:
                pass

        def on_error(ws, error):
            logger.error("WS error [%s]: %s", channel, error)

        def on_close(ws, code, msg):
            logger.info("WS closed [%s]: %s", channel, code)

        def on_open(ws):
            logger.info("WS connected [%s]", channel)

        return on_message, on_error, on_close, on_open

    def connect_pnl(self, bot_id: str):
        if not WS_AVAILABLE:
            return
        url = f"{self.base_url}/ws/pnl/{bot_id}"
        self._start_connection("pnl", url)

    def connect_trades(self, bot_id: str):
        if not WS_AVAILABLE:
            return
        url = f"{self.base_url}/ws/trades/{bot_id}"
        self._start_connection("trades", url)

    def connect_signals(self, bot_id: str):
        if not WS_AVAILABLE:
            return
        url = f"{self.base_url}/ws/signals/{bot_id}"
        self._start_connection("signals", url)

    def connect_bots(self):
        if not WS_AVAILABLE:
            return
        url = f"{self.base_url}/ws/bots"
        self._start_connection("bots", url)

    def connect_all(self):
        if not WS_AVAILABLE:
            return
        url = f"{self.base_url}/ws/realtime"
        self._start_connection("all", url)

    def _start_connection(self, channel: str, url: str):
        if channel in self._threads and self._threads[channel].is_alive():
            return

        on_msg, on_err, on_close, on_open = self._make_handler(channel)

        def run():
            while self._running:
                try:
                    ws = websocket.WebSocketApp(
                        url, on_message=on_msg, on_error=on_err,
                        on_close=on_close, on_open=on_open,
                    )
                    self._connections[channel] = ws
                    ws.run_forever(ping_interval=30)
                except Exception as e:
                    logger.error("WS reconnect [%s]: %s", channel, e)
                time.sleep(5)

        self._running = True
        t = threading.Thread(target=run, daemon=True, name=f"ws-{channel}")
        self._threads[channel] = t
        t.start()

    def disconnect_all(self):
        self._running = False
        for ws in self._connections.values():
            try:
                ws.close()
            except Exception:
                pass

    def get_latest(self, channel: str) -> Optional[dict]:
        return self._latest_data.get(channel)

    @property
    def is_connected(self) -> bool:
        return any(t.is_alive() for t in self._threads.values())
