"""Prometheus metrics exporter for OdaTrade."""
import time
from typing import Dict

_start_time = time.time()

_counters: Dict[str, int] = {
    "trades_total": 0,
    "signals_total": 0,
    "orders_total": 0,
    "errors_total": 0,
    "ws_connections": 0,
    "bots_running": 0,
}

_gauges: Dict[str, float] = {
    "pnl_total": 0.0,
    "balance_total": 0.0,
    "drawdown_pct": 0.0,
}


def increment(metric: str, amount: int = 1):
    _counters[metric] = _counters.get(metric, 0) + amount


def set_gauge(metric: str, value: float):
    _gauges[metric] = value


def render_metrics() -> str:
    lines = []
    uptime = time.time() - _start_time
    lines.append("# HELP odatrade_up OdaTrade service is running")
    lines.append("# TYPE odatrade_up gauge")
    lines.append("odatrade_up 1")
    lines.append("# HELP odatrade_uptime_seconds Service uptime")
    lines.append("# TYPE odatrade_uptime_seconds gauge")
    lines.append(f"odatrade_uptime_seconds {uptime:.1f}")

    for name, val in _counters.items():
        lines.append(f"# HELP odatrade_{name} Total {name}")
        lines.append(f"# TYPE odatrade_{name} counter")
        lines.append(f"odatrade_{name} {val}")

    for name, val in _gauges.items():
        lines.append(f"# HELP odatrade_{name} Current {name}")
        lines.append(f"# TYPE odatrade_{name} gauge")
        lines.append(f"odatrade_{name} {val}")

    return "\n".join(lines) + "\n"


def sync_from_bot_manager():
    try:
        from backend.api.routes.bots_api import get_bot_manager
        mgr = get_bot_manager()
        agg = mgr.get_aggregate_metrics()
        _counters["bots_running"] = agg.get("running_bots", 0)
        _counters["trades_total"] = agg.get("total_trades", 0)
        set_gauge("pnl_total", agg.get("aggregate_pnl", 0))
    except Exception:
        pass
