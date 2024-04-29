"""Reporting API for OdaTrade performance analytics."""
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from backend.auth.middleware import require_auth

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/daily", dependencies=[Depends(require_auth)])
def daily_report(bot_id: Optional[str] = None, days: int = Query(7, le=90)):
    try:
        from backend.api.dependencies import get_postgres_pool
        pool = get_postgres_pool()
        if not pool:
            return {"error": "Database not available", "days": days}
        from backend.db.repositories.trades import TradeRepository
        repo = TradeRepository(pool)
        stats = repo.stats(bot_id)
        trades = repo.list_trades(bot_id=bot_id, limit=days * 50)
        return {
            "period_days": days,
            "bot_id": bot_id,
            "stats": stats,
            "recent_trades": trades[:20],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {"error": str(e), "days": days}


@router.get("/performance", dependencies=[Depends(require_auth)])
def performance_report(bot_id: Optional[str] = None):
    try:
        from backend.api.routes.bots_api import get_bot_manager
        mgr = get_bot_manager()
        if bot_id:
            status = mgr.get_bot_status(bot_id)
            return {"bot_id": bot_id, "performance": status}
        agg = mgr.get_aggregate_metrics()
        bots = mgr.list_bots()
        return {
            "aggregate": agg,
            "bots": bots,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/risk", dependencies=[Depends(require_auth)])
def risk_report(bot_id: Optional[str] = None):
    try:
        from backend.api.dependencies import get_state_store
        state = get_state_store()
        if bot_id:
            return {
                "bot_id": bot_id,
                "kill_switch": state.is_kill_switch_active(bot_id),
                "positions": state.get_positions(bot_id),
                "metrics": state.get_metrics(bot_id),
                "pnl": state.get_pnl(bot_id),
            }
        from backend.api.routes.bots_api import get_bot_manager
        mgr = get_bot_manager()
        reports = []
        for bot in mgr.list_bots():
            bid = bot["bot_id"]
            reports.append({
                "bot_id": bid,
                "name": bot["name"],
                "kill_switch": state.is_kill_switch_active(bid),
                "metrics": state.get_metrics(bid),
            })
        return {"bots": reports, "generated_at": datetime.now(timezone.utc).isoformat()}
    except Exception as e:
        return {"error": str(e)}
