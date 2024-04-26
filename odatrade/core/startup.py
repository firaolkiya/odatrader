"""OdaTrade platform startup and shutdown orchestration."""
import asyncio
import logging
import os
import signal
import sys
from typing import Optional

logger = logging.getLogger("odatrade.startup")


class PlatformBootstrap:
    """Initializes all OdaTrade services in correct order."""

    def __init__(self):
        self.redis_client = None
        self.postgres_pool = None
        self.event_bus = None
        self.bot_manager = None
        self._running = False

    async def initialize(self):
        logger.info("OdaTrade platform initializing...")

        # 1. Redis
        from odatrade.core.redis_client import RedisClient
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis_client = RedisClient.get_instance(redis_url)
        redis_ok = self.redis_client.connect()
        logger.info("Redis: %s", "connected" if redis_ok else "fallback mode")

        # 2. PostgreSQL
        db_url = os.getenv("DATABASE_URL", "")
        if db_url and "postgresql" in db_url:
            from backend.db.postgres_pool import PostgresPool
            self.postgres_pool = PostgresPool(db_url)
            pg_ok = self.postgres_pool.connect()
            if pg_ok:
                self.postgres_pool.init_tables()
            logger.info("PostgreSQL: %s", "connected" if pg_ok else "failed")

        # 3. Event bus
        backend = os.getenv("EVENT_BACKEND", "redis")
        from odatrade.core.event_bus_async import create_event_bus
        self.event_bus = create_event_bus(backend=backend, redis_url=redis_url)
        await self.event_bus.start()
        logger.info("EventBus: started (backend=%s)", backend)

        # 4. Bot manager
        from backend.bots.manager import BotManager
        self.bot_manager = BotManager(redis_url=redis_url, event_backend=backend)
        self.bot_manager.start_platform()
        logger.info("BotManager: ready")

        self._running = True
        logger.info("OdaTrade platform ready")

    async def shutdown(self):
        logger.info("OdaTrade platform shutting down...")
        if self.bot_manager:
            self.bot_manager.stop_all()
        if self.event_bus:
            await self.event_bus.stop()
        if self.postgres_pool:
            self.postgres_pool.close()
        if self.redis_client:
            self.redis_client.close()
        self._running = False
        logger.info("OdaTrade platform stopped")

    def setup_signal_handlers(self, loop: asyncio.AbstractEventLoop):
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.shutdown()))


_bootstrap: Optional[PlatformBootstrap] = None


def get_bootstrap() -> PlatformBootstrap:
    global _bootstrap
    if _bootstrap is None:
        _bootstrap = PlatformBootstrap()
    return _bootstrap


async def run_platform():
    bootstrap = get_bootstrap()
    await bootstrap.initialize()
    bootstrap.setup_signal_handlers(asyncio.get_event_loop())
    while bootstrap._running:
        await asyncio.sleep(1)
