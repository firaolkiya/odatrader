"""Admin API for platform management."""
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from backend.auth.middleware import require_auth

logger = logging.getLogger("odatrade.admin")
router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin(auth=Depends(require_auth)):
    role = auth.get("role", "viewer")
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return auth


class PlatformConfig(BaseModel):
    event_backend: str = "redis"
    max_bots: int = 10
    default_risk_profile: str = "moderate"


@router.get("/platform", dependencies=[Depends(require_admin)])
def platform_info():
    from odatrade.core.startup import get_bootstrap
    bootstrap = get_bootstrap()
    return {
        "running": bootstrap._running,
        "redis": bootstrap.redis_client.is_connected if bootstrap.redis_client else False,
        "postgres": bootstrap.postgres_pool.is_connected if bootstrap.postgres_pool else False,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/platform/restart", dependencies=[Depends(require_admin)])
async def restart_platform():
    from odatrade.core.startup import get_bootstrap
    bootstrap = get_bootstrap()
    await bootstrap.shutdown()
    await bootstrap.initialize()
    return {"status": "restarted"}


@router.get("/deployments", dependencies=[Depends(require_admin)])
def list_deployments():
    from backend.bots.cloud_deployer import CloudDeployer
    deployer = CloudDeployer(provider=os.getenv("CLOUD_PROVIDER", "docker"))
    from backend.api.routes.bots_api import get_bot_manager
    mgr = get_bot_manager()
    deployments = []
    for bot in mgr.list_bots():
        spec = deployer.create_spec(bot["bot_id"], bot["name"], bot)
        deployments.append({
            "bot_id": bot["bot_id"],
            "name": bot["name"],
            "spec": {"provider": spec.cloud_provider, "image": spec.image},
        })
    return {"deployments": deployments}


@router.get("/event-bus/stats", dependencies=[Depends(require_admin)])
def event_bus_stats():
    from odatrade.core.startup import get_bootstrap
    bootstrap = get_bootstrap()
    if not bootstrap.event_bus:
        return {"status": "not_initialized"}
    return {
        "backends": len(bootstrap.event_bus.backends),
        "started": bootstrap.event_bus._started,
        "handlers": {k.value: len(v) for k, v in bootstrap.event_bus._handlers.items()},
    }


@router.post("/cache/flush", dependencies=[Depends(require_admin)])
def flush_redis_cache():
    from backend.api.dependencies import get_redis_client
    client = get_redis_client()
    if not client.is_connected:
        return {"status": "redis_unavailable"}
    keys = client.client.keys("odatrade:*")
    if keys:
        client.client.delete(*keys)
    return {"status": "flushed", "keys_deleted": len(keys)}


import os
