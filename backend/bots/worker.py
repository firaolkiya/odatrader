"""Bot worker: runs market data ingestion in isolated thread per bot."""
import logging
import threading
import time
from typing import Optional

from backend.bots.config import BotConfig
from backend.events.pipeline import PipelineManager
from odatrade.core.redis_state import RedisStateStore

logger = logging.getLogger("odatrade.bot_worker")


class BotWorker:
    """Per-bot worker thread that feeds market data into the event pipeline."""

    def __init__(self, bot_id: str, config: BotConfig, pipeline_manager: PipelineManager, state: RedisStateStore):
        self.bot_id = bot_id
        self.config = config
        self.pipeline_manager = pipeline_manager
        self.state = state
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._ws_manager = None

    @property
    def is_alive(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self):
        if self.is_alive:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, name=f"odatrade-bot-{self.bot_id}", daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._ws_manager:
            try:
                self._ws_manager.stop()
            except Exception:
                pass
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("[%s] Worker stopped", self.bot_id)

    def _run(self):
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.pipeline_manager.start_pipeline(self.bot_id))
        try:
            self._start_websocket_feed(loop)
        except Exception as e:
            logger.error("[%s] Worker error: %s", self.bot_id, e)
            self._simulate_feed(loop)
        finally:
            loop.run_until_complete(self.pipeline_manager.stop_pipeline(self.bot_id))
            loop.close()

    def _start_websocket_feed(self, loop):
        from binance import ThreadedWebsocketManager
        self._ws_manager = ThreadedWebsocketManager()
        self._ws_manager.start()

        def on_kline(msg):
            if not self._running:
                return
            if msg.get("e") != "kline":
                return
            k = msg["k"]
            if not k.get("x"):
                return
            symbol = k["s"].lower()
            candle = {
                "t": k["t"], "o": k["o"], "h": k["h"],
                "l": k["l"], "c": k["c"], "v": k["v"],
            }
            asyncio.run_coroutine_threadsafe(
                self.pipeline_manager.ingest_candle(self.bot_id, symbol, candle), loop
            )

        for symbol in self.config.symbols:
            self._ws_manager.start_kline_socket(
                callback=on_kline,
                symbol=symbol.upper(),
                interval=self.config.interval,
            )
        logger.info("[%s] WebSocket feed started for %s", self.bot_id, self.config.symbols)
        while self._running:
            time.sleep(1)

    def _simulate_feed(self, loop):
        """Fallback simulated feed when Binance WS unavailable."""
        import random
        prices = {s: 50000.0 if "btc" in s else 3000.0 for s in self.config.symbols}
        logger.info("[%s] Using simulated market data feed", self.bot_id)
        tick = 0
        while self._running:
            for symbol in self.config.symbols:
                prices[symbol] *= 1 + random.uniform(-0.001, 0.001)
                candle = {
                    "t": int(time.time() * 1000),
                    "o": str(prices[symbol]),
                    "h": str(prices[symbol] * 1.001),
                    "l": str(prices[symbol] * 0.999),
                    "c": str(prices[symbol]),
                    "v": str(random.uniform(1, 100)),
                }
                asyncio.run_coroutine_threadsafe(
                    self.pipeline_manager.ingest_candle(self.bot_id, symbol, candle), loop
                )
            tick += 1
            time.sleep(5)
