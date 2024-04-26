"""Multi-bot orchestrator with isolated event pipelines."""
import asyncio
import logging
import threading
from typing import Dict, List, Optional

from backend.bots.config import BotConfig, apply_risk_profile
from backend.bots.registry import BotRegistry
from backend.bots.worker import BotWorker
from backend.events.pipeline import PipelineManager
from odatrade.core.event_bus_async import AsyncEventBus, create_event_bus
from odatrade.core.redis_client import RedisClient
from odatrade.core.redis_state import RedisStateStore

logger = logging.getLogger("odatrade.bot_manager")


class BotManager:
    """
    Orchestrates multiple trading bots, each with:
    - Isolated config (strategy, risk profile, assets)
    - Dedicated event pipeline
    - Independent Redis state namespace
    - Optional container isolation for cloud deployment
    """

    def __init__(self, redis_url: str = "redis://localhost:6379/0", event_backend: str = "redis"):
        self.redis = RedisClient.get_instance(redis_url)
        self.redis.connect()
        self.state = RedisStateStore(self.redis)
        self.event_bus = create_event_bus(backend=event_backend, redis_url=redis_url)
        self.registry = BotRegistry(self.state)
        self.pipeline_manager = PipelineManager(self.event_bus, self.state)
        self._workers: Dict[str, BotWorker] = {}
        self._started = False
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None

    def _ensure_loop(self):
        if self._loop is None or not self._loop.is_running():
            self._loop = asyncio.new_event_loop()
            self._thread = threading.Thread(target=self._loop.run_forever, daemon=True)
            self._thread.start()

    def _run_async(self, coro):
        self._ensure_loop()
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result(timeout=30)

    async def _async_start(self):
        await self.event_bus.start()
        self._started = True

    def start_platform(self):
        self._run_async(self._async_start())
        logger.info("OdaTrade platform started")

    def create_bot(self, config: BotConfig) -> BotConfig:
        config = apply_risk_profile(config)
        self.registry.register(config)
        pipeline_config = config.to_dict()
        self._run_async(self.pipeline_manager.create_pipeline(config.bot_id, pipeline_config))
        return config

    def start_bot(self, bot_id: str) -> dict:
        config = self.registry.get(bot_id)
        if not config:
            raise ValueError(f"Bot {bot_id} not found")

        worker = BotWorker(bot_id, config, self.pipeline_manager, self.state)
        self._workers[bot_id] = worker
        worker.start()
        self.registry.update_status(bot_id, "running")
        logger.info("Bot started: %s (%s)", bot_id, config.name)
        return {"bot_id": bot_id, "status": "running", "name": config.name}

    def stop_bot(self, bot_id: str) -> dict:
        worker = self._workers.pop(bot_id, None)
        if worker:
            worker.stop()
        self._run_async(self.pipeline_manager.stop_pipeline(bot_id))
        self.registry.update_status(bot_id, "stopped")
        return {"bot_id": bot_id, "status": "stopped"}

    def stop_all(self):
        for bot_id in list(self._workers.keys()):
            self.stop_bot(bot_id)
        self._run_async(self.pipeline_manager.stop_all())

    def get_bot_status(self, bot_id: str) -> dict:
        config = self.registry.get(bot_id)
        status = self.state.get_bot_status(bot_id) or {}
        worker = self._workers.get(bot_id)
        pipeline = self.pipeline_manager.get_pipeline(bot_id)
        return {
            "bot_id": bot_id,
            "name": config.name if config else "unknown",
            "status": status.get("status", "unknown"),
            "worker_alive": worker.is_alive if worker else False,
            "pipeline_running": pipeline.is_running if pipeline else False,
            "metrics": self.state.get_metrics(bot_id),
            "positions": self.state.get_positions(bot_id),
            "pnl": self.state.get_pnl(bot_id),
        }

    def list_bots(self) -> List[dict]:
        return self.registry.list_all()

    def get_aggregate_metrics(self) -> dict:
        bots = self.registry.list_all()
        total_pnl = 0.0
        total_trades = 0
        running = 0
        for bot in bots:
            if bot.get("status") == "running":
                running += 1
            metrics = self.state.get_metrics(bot["bot_id"])
            total_trades += metrics.get("orders_filled", 0)
            pnl_data = self.state.get_pnl(bot["bot_id"])
            if isinstance(pnl_data, dict):
                for v in pnl_data.values():
                    if isinstance(v, dict):
                        total_pnl += v.get("cumulative", 0)
        return {
            "total_bots": len(bots),
            "running_bots": running,
            "total_trades": total_trades,
            "aggregate_pnl": total_pnl,
        }
