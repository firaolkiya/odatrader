"""Multi-bot management API."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.auth.middleware import require_auth
from backend.bots.config import BotConfig
from backend.bots.manager import BotManager

router = APIRouter(prefix="/bots", tags=["bots"])

_bot_manager: Optional[BotManager] = None


def get_bot_manager() -> BotManager:
    global _bot_manager
    if _bot_manager is None:
        from config.config import DATABASE_URL
        import os
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        _bot_manager = BotManager(redis_url=redis_url)
        _bot_manager.start_platform()
    return _bot_manager


class CreateBotRequest(BaseModel):
    name: str
    symbols: List[str] = ["btcusdt"]
    strategy: str = "strategy_voter"
    risk_profile: str = "moderate"
    starting_balance: float = 5000.0


class BotResponse(BaseModel):
    bot_id: str
    name: str
    status: str
    symbols: List[str] = []


@router.get("/", dependencies=[Depends(require_auth)])
def list_bots():
    mgr = get_bot_manager()
    return {"bots": mgr.list_bots(), "aggregate": mgr.get_aggregate_metrics()}


@router.post("/", dependencies=[Depends(require_auth)])
def create_bot(req: CreateBotRequest):
    mgr = get_bot_manager()
    config = BotConfig(
        name=req.name,
        symbols=req.symbols,
        strategy=req.strategy,
        risk_profile=req.risk_profile,
        starting_balance=req.starting_balance,
    )
    config = mgr.create_bot(config)
    return {"bot_id": config.bot_id, "name": config.name, "status": "created"}


@router.post("/{bot_id}/start", dependencies=[Depends(require_auth)])
def start_bot(bot_id: str):
    mgr = get_bot_manager()
    try:
        return mgr.start_bot(bot_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{bot_id}/stop", dependencies=[Depends(require_auth)])
def stop_bot(bot_id: str):
    mgr = get_bot_manager()
    return mgr.stop_bot(bot_id)


@router.get("/{bot_id}", dependencies=[Depends(require_auth)])
def get_bot(bot_id: str):
    mgr = get_bot_manager()
    try:
        return mgr.get_bot_status(bot_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/stop-all", dependencies=[Depends(require_auth)])
def stop_all_bots():
    mgr = get_bot_manager()
    mgr.stop_all()
    return {"status": "all_stopped"}
