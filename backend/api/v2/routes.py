"""OdaTrade API v2 — multi-bot, event-driven endpoints."""
from fastapi import APIRouter, Depends
from backend.auth.middleware import require_auth

router = APIRouter(prefix="/api/v2", tags=["OdaTrade v2"])


@router.get("/status")
def v2_status():
    return {
        "version": "2.0",
        "name": "OdaTrade",
        "features": [
            "multi-bot", "redis-eventbus", "websocket-realtime",
            "jwt-auth", "postgres-pool", "cloud-deployment",
            "llm-news-ingestion", "monitoring",
        ],
        "architecture": "event-driven",
        "event_flow": "market_data → strategies → risk → orders → pnl",
    }


@router.get("/bots", dependencies=[Depends(require_auth)])
def v2_list_bots():
    from backend.api.routes.bots_api import get_bot_manager
    mgr = get_bot_manager()
    return {"bots": mgr.list_bots(), "aggregate": mgr.get_aggregate_metrics()}


@router.get("/monitoring", dependencies=[Depends(require_auth)])
def v2_monitoring():
    from backend.api.routes.monitoring import bots_monitoring_summary
    return bots_monitoring_summary()


@router.get("/news/sentiment")
def v2_news_sentiment():
    from backend.api.routes.news_api import get_ingestor
    ingestor = get_ingestor()
    return ingestor.ingest_and_analyze(["BTC", "ETH"])
