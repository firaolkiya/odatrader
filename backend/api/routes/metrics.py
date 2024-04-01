"""Prometheus-style metrics endpoint."""
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter(prefix="/metrics", tags=["metrics"])

_count = {"trades_total": 0, "signals_total": 0}

@router.get("/", response_class=PlainTextResponse)
def prometheus_metrics():
    lines = [f"# HELP odatrade_trades_total Total trades", f"odatrade_trades_total {_count['trades_total']}"]
    return "\n".join(lines)
