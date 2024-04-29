"""Monitoring and observability endpoints."""
import os
import time
import psutil
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

_start_time = time.time()


@router.get("/health")
def detailed_health():
    from backend.api.routes.ws_realtime import manager
    return {
        "status": "healthy",
        "service": "OdaTrade",
        "version": "2.0.0",
        "uptime_seconds": round(time.time() - _start_time, 1),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "websocket_connections": manager.connection_count,
    }


@router.get("/system")
def system_metrics():
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        return {
            "cpu_percent": cpu,
            "memory": {
                "total_gb": round(mem.total / 1e9, 2),
                "used_gb": round(mem.used / 1e9, 2),
                "percent": mem.percent,
            },
            "disk": {
                "total_gb": round(disk.total / 1e9, 2),
                "used_gb": round(disk.used / 1e9, 2),
                "percent": disk.percent,
            },
        }
    except Exception:
        return {"cpu_percent": 0, "memory": {}, "disk": {}}


@router.get("/services")
def service_status():
    results = {}
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    db_url = os.getenv("DATABASE_URL", "")

    try:
        from odatrade.core.redis_client import RedisClient
        client = RedisClient.get_instance(redis_url)
        results["redis"] = {"status": "healthy" if client.connect() else "unavailable"}
    except Exception as e:
        results["redis"] = {"status": "error", "message": str(e)}

    try:
        from backend.db.postgres_pool import PostgresPool
        pool = PostgresPool(db_url)
        results["postgres"] = pool.health_check()
    except Exception as e:
        results["postgres"] = {"status": "error", "message": str(e)}

    try:
        from backend.api.routes.bots_api import get_bot_manager
        mgr = get_bot_manager()
        results["bots"] = mgr.get_aggregate_metrics()
    except Exception as e:
        results["bots"] = {"status": "error", "message": str(e)}

    return results


@router.get("/bots/summary")
def bots_monitoring_summary():
    try:
        from backend.api.routes.bots_api import get_bot_manager
        mgr = get_bot_manager()
        bots = mgr.list_bots()
        details = []
        for bot in bots:
            status = mgr.get_bot_status(bot["bot_id"])
            details.append(status)
        return {
            "aggregate": mgr.get_aggregate_metrics(),
            "bots": details,
        }
    except Exception as e:
        return {"error": str(e), "bots": []}
