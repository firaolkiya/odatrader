"""OdaTrade FastAPI application — cloud-ready, multi-bot, event-driven."""
import logging
import os
import sys
from contextlib import asynccontextmanager

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.router import api_router
from backend.api.routes.health import router as health_router
from backend.api.routes.portfolio import router as portfolio_router
from backend.api.routes.trades import router as trades_router
from backend.api.routes.strategies_api import router as strategies_router
from backend.api.routes.backtest_api import router as backtest_router
from backend.api.routes.alerts_api import router as alerts_router
from backend.api.routes.metrics import router as metrics_router
from backend.api.routes.ws_prices import router as ws_router
from backend.api.routes.ws_realtime import router as ws_realtime_router
from backend.api.routes.auth import router as auth_router
from backend.api.routes.bots_api import router as bots_router
from backend.api.routes.monitoring import router as monitoring_router
from backend.api.routes.news_api import router as news_router
from backend.api.routes.reports import router as reports_router
from backend.api.routes.admin import router as admin_router
from backend.api.routes.instruments_api import router as instruments_router
from backend.api.routes.orders_api import router as orders_router
from backend.api.routes.config_api import router as config_router
from backend.api.routes.pnl_metrics import router as pnl_metrics_router
from backend.api.routes.ws_quotes_trades import router as ws_qt_router
from backend.api.routes.signals_api import router as signals_router
from backend.api.routes.strategy_control import router as strategy_ctrl_router
from backend.api.v2.routes import router as v2_router
from backend.api.middleware.error_handler import ErrorHandlerMiddleware, RetryMiddleware
from config.config import DATABASE_URL, JWT_SECRET

logger = logging.getLogger("odatrade.api")

# Global services
postgres_pool = None
redis_client = None
bot_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global postgres_pool, redis_client, bot_manager

    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    from odatrade.core.redis_client import RedisClient
    redis_client = RedisClient.get_instance(redis_url)
    redis_client.connect()

    if DATABASE_URL and "postgresql" in DATABASE_URL:
        from backend.db.postgres_pool import PostgresPool
        postgres_pool = PostgresPool(DATABASE_URL)
        if postgres_pool.connect():
            postgres_pool.init_tables()
            from backend.db.repositories.trades import TradeRepository
            from backend.db.repositories.signals import SignalRepository
            from backend.db.repositories.market import MarketDataRepository
            TradeRepository(postgres_pool).ensure_table()
            SignalRepository(postgres_pool).ensure_table()
            MarketDataRepository(postgres_pool).ensure_table()

    logger.info("OdaTrade API started (redis=%s, postgres=%s)",
                redis_client.is_connected, postgres_pool.is_connected if postgres_pool else False)
    yield

    if postgres_pool:
        postgres_pool.close()
    if redis_client:
        redis_client.close()
    logger.info("OdaTrade API shutdown")


app = FastAPI(
    title="OdaTrade API",
    version="2.0.0",
    description="Scalable event-driven crypto trading platform",
    lifespan=lifespan,
)

app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RetryMiddleware, max_retries=3)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Core routes
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(api_router)
app.include_router(portfolio_router)
app.include_router(trades_router)
app.include_router(strategies_router)
app.include_router(backtest_router)
app.include_router(alerts_router)
app.include_router(metrics_router)
app.include_router(ws_router)
app.include_router(ws_realtime_router)
app.include_router(bots_router)
app.include_router(monitoring_router)
app.include_router(news_router)
app.include_router(reports_router)
app.include_router(admin_router)
app.include_router(instruments_router)
app.include_router(orders_router)
app.include_router(config_router)
app.include_router(pnl_metrics_router)
app.include_router(ws_qt_router)
app.include_router(signals_router)
app.include_router(strategy_ctrl_router)
app.include_router(v2_router)


@app.get("/status")
def status():
    from backend.api.routes.bots_api import get_bot_manager
    try:
        mgr = get_bot_manager()
        agg = mgr.get_aggregate_metrics()
        return {
            "service": "OdaTrade",
            "version": "2.0.0",
            "running_bots": agg.get("running_bots", 0),
            "total_bots": agg.get("total_bots", 0),
            "redis": redis_client.is_connected if redis_client else False,
            "postgres": postgres_pool.is_connected if postgres_pool else False,
        }
    except Exception:
        return {"service": "OdaTrade", "version": "2.0.0", "running_bots": 0}
