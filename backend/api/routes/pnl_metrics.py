"""PnL and risk metrics API."""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from backend.auth.middleware import require_auth

router = APIRouter(prefix="/metrics", tags=["pnl-metrics"])


@router.get("/pnl", dependencies=[Depends(require_auth)])
def pnl_metrics(window: str = Query("1d", pattern="^(1d|1w|MTD|YTD|all)$"), bot_id: Optional[str] = None):
    try:
        from backend.api.routes.bots_api import get_bot_manager
        mgr = get_bot_manager()
        if bot_id:
            status = mgr.get_bot_status(bot_id)
            pnl = status.get("pnl", {})
            return {"window": window, "bot_id": bot_id, "pnl": pnl, "metrics": status.get("metrics", {})}
        agg = mgr.get_aggregate_metrics()
        return {"window": window, "aggregate": agg}
    except Exception as e:
        return {"window": window, "error": str(e), "pnl": 0}


@router.get("/risk", dependencies=[Depends(require_auth)])
def risk_metrics(bot_id: Optional[str] = None):
    try:
        from backend.api.dependencies import get_state_store
        state = get_state_store()
        if bot_id:
            return {
                "bot_id": bot_id,
                "kill_switch": state.is_kill_switch_active(bot_id),
                "positions": state.get_positions(bot_id),
                "metrics": state.get_metrics(bot_id),
            }
        from backend.api.routes.bots_api import get_bot_manager
        mgr = get_bot_manager()
        risk_data = []
        for bot in mgr.list_bots():
            bid = bot["bot_id"]
            risk_data.append({
                "bot_id": bid, "name": bot["name"],
                "kill_switch": state.is_kill_switch_active(bid),
                "metrics": state.get_metrics(bid),
            })
        return {"bots": risk_data}
    except Exception as e:
        return {"error": str(e)}
