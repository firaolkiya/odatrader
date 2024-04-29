"""Order management API (POST/DELETE orders)."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.auth.middleware import require_auth
from backend.core.signals import TradeIntent
from backend.exec.router import ExecutionRouter
from datetime import datetime, timezone

router = APIRouter(tags=["orders"])
_exec_router: Optional[ExecutionRouter] = None


def get_exec_router() -> ExecutionRouter:
    global _exec_router
    if _exec_router is None:
        import os
        mode = os.getenv("TRADING_MODE", "paper")
        _exec_router = ExecutionRouter(mode=mode)
    return _exec_router


class OrderRequest(BaseModel):
    symbol: str
    side: str
    qty: float
    type: str = "limit"
    px: Optional[float] = None
    stop_px: Optional[float] = None
    tif: str = "GTC"
    post_only: bool = False
    reduce_only: bool = False


@router.post("/orders", dependencies=[Depends(require_auth)])
async def create_order(req: OrderRequest):
    exec_r = get_exec_router()
    intent = TradeIntent(
        ts=datetime.now(timezone.utc).isoformat(),
        instrument=req.symbol, side=req.side, size=req.qty,
        order_type=req.type, px_hint=req.px, stop_px=req.stop_px,
        tif=req.tif, post_only=req.post_only, reduce_only=req.reduce_only,
    )
    result = await exec_r.route_intent(intent)
    return result


@router.delete("/orders/{clid}", dependencies=[Depends(require_auth)])
async def cancel_order(clid: str):
    exec_r = get_exec_router()
    open_orders = exec_r.order_manager.list_open()
    for o in open_orders:
        if o.id == clid:
            exec_r.order_manager.cancel(clid)
            return {"cancelled": clid}
    raise HTTPException(status_code=404, detail="Order not found")


@router.get("/orders", dependencies=[Depends(require_auth)])
def list_orders():
    exec_r = get_exec_router()
    return {"open": [{"id": o.id, "symbol": o.symbol, "side": o.side.value, "qty": o.quantity,
                       "status": o.status.value} for o in exec_r.order_manager.list_open()]}


@router.get("/positions", dependencies=[Depends(require_auth)])
def get_positions():
    try:
        from backend.api.routes.bots_api import get_bot_manager
        mgr = get_bot_manager()
        bots = mgr.list_bots()
        positions = {}
        for bot in bots:
            status = mgr.get_bot_status(bot["bot_id"])
            positions[bot["bot_id"]] = status.get("positions", {})
        return {"positions": positions}
    except Exception:
        return {"positions": {}}
