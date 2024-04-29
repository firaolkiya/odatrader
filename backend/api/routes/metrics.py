"""Prometheus-style metrics endpoint."""
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from backend.monitoring.prometheus_exporter import render_metrics, sync_from_bot_manager

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/", response_class=PlainTextResponse)
def prometheus_metrics():
    sync_from_bot_manager()
    return render_metrics()


@router.get("/json")
def metrics_json():
    sync_from_bot_manager()
    from backend.monitoring.prometheus_exporter import _counters, _gauges
    return {"counters": dict(_counters), "gauges": dict(_gauges)}
