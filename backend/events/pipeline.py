"""Event-driven trading pipeline: market data → strategies → risk → orders → PnL."""
import asyncio
import logging
import uuid
from typing import Any, Dict, Optional

from odatrade.core.event_bus_async import AsyncEventBus, Event, EventType
from odatrade.core.redis_state import RedisStateStore
from backend.events.handlers.market_data import MarketDataHandler
from backend.events.handlers.strategy import StrategyHandler
from backend.events.handlers.risk import RiskHandler
from backend.events.handlers.orders import OrderHandler
from backend.events.handlers.pnl import PnLHandler

logger = logging.getLogger("odatrade.pipeline")


class TradingPipeline:
    """
    Modular event flow orchestrator.
    Each stage is an async handler subscribed to specific event types.
    Events flow: MARKET_DATA → FEATURES_READY → STRATEGY_SIGNAL →
                 RISK_CHECK → RISK_APPROVED → ORDER_CREATED → ORDER_FILLED → PNL_UPDATE
    """

    def __init__(self, bot_id: str, config: dict, event_bus: AsyncEventBus, state_store: RedisStateStore):
        self.bot_id = bot_id
        self.config = config
        self.bus = event_bus
        self.state = state_store
        self._running = False
        self._handlers = self._build_handlers()

    def _build_handlers(self) -> Dict[str, Any]:
        return {
            "market_data": MarketDataHandler(self.bot_id, self.config, self.bus, self.state),
            "strategy": StrategyHandler(self.bot_id, self.config, self.bus, self.state),
            "risk": RiskHandler(self.bot_id, self.config, self.bus, self.state),
            "orders": OrderHandler(self.bot_id, self.config, self.bus, self.state),
            "pnl": PnLHandler(self.bot_id, self.config, self.bus, self.state),
        }

    def _register_handlers(self):
        h = self._handlers
        self.bus.on(EventType.MARKET_DATA, h["market_data"].handle)
        self.bus.on(EventType.FEATURES_READY, h["strategy"].handle)
        self.bus.on(EventType.STRATEGY_SIGNAL, h["risk"].handle)
        self.bus.on(EventType.RISK_APPROVED, h["orders"].handle)
        self.bus.on(EventType.ORDER_FILLED, h["pnl"].handle)
        self.bus.on(EventType.KILL_SWITCH, self._on_kill_switch)

    async def _on_kill_switch(self, event: Event):
        logger.warning("[%s] Kill switch activated: %s", self.bot_id, event.payload)
        self._running = False
        self.state.activate_kill_switch(self.bot_id, event.payload.get("reason", ""))

    async def start(self):
        self._register_handlers()
        self._running = True
        self.state.set_bot_status(self.bot_id, "running", {"config": self.config})
        await self.bus.emit(Event(
            type=EventType.BOT_STARTED,
            bot_id=self.bot_id,
            payload={"config": self.config},
        ))
        logger.info("[%s] Pipeline started", self.bot_id)

    async def stop(self):
        self._running = False
        self.state.set_bot_status(self.bot_id, "stopped")
        await self.bus.emit(Event(type=EventType.BOT_STOPPED, bot_id=self.bot_id))
        logger.info("[%s] Pipeline stopped", self.bot_id)

    async def ingest_candle(self, symbol: str, candle: dict):
        """Entry point for market data into the pipeline."""
        if not self._running:
            return
        if self.state.is_kill_switch_active(self.bot_id):
            return
        cid = str(uuid.uuid4())[:8]
        await self.bus.emit(Event(
            type=EventType.MARKET_DATA,
            bot_id=self.bot_id,
            payload={"symbol": symbol, "candle": candle},
            correlation_id=cid,
        ))

    @property
    def is_running(self) -> bool:
        return self._running


class PipelineManager:
    """Manages multiple isolated trading pipelines (one per bot)."""

    def __init__(self, event_bus: AsyncEventBus, state_store: RedisStateStore):
        self.bus = event_bus
        self.state = state_store
        self._pipelines: Dict[str, TradingPipeline] = {}

    async def create_pipeline(self, bot_id: str, config: dict) -> TradingPipeline:
        if bot_id in self._pipelines:
            raise ValueError(f"Pipeline already exists for bot {bot_id}")
        pipeline = TradingPipeline(bot_id, config, self.bus, self.state)
        self._pipelines[bot_id] = pipeline
        return pipeline

    async def start_pipeline(self, bot_id: str):
        pipeline = self._pipelines.get(bot_id)
        if not pipeline:
            raise ValueError(f"No pipeline for bot {bot_id}")
        await pipeline.start()

    async def stop_pipeline(self, bot_id: str):
        pipeline = self._pipelines.get(bot_id)
        if pipeline:
            await pipeline.stop()

    async def stop_all(self):
        for bot_id in list(self._pipelines.keys()):
            await self.stop_pipeline(bot_id)

    def get_pipeline(self, bot_id: str) -> Optional[TradingPipeline]:
        return self._pipelines.get(bot_id)

    def list_pipelines(self) -> Dict[str, dict]:
        return {
            bot_id: {
                "running": p.is_running,
                "config": p.config,
            }
            for bot_id, p in self._pipelines.items()
        }

    async def ingest_candle(self, bot_id: str, symbol: str, candle: dict):
        pipeline = self._pipelines.get(bot_id)
        if pipeline:
            await pipeline.ingest_candle(symbol, candle)
