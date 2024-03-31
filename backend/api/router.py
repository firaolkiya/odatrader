"""Unified OdaTrade API router."""
from fastapi import APIRouter

api_router = APIRouter(prefix="/api/v1", tags=["OdaTrade"])

@api_router.get("/info")
def api_info():
    return {"name": "OdaTrade", "version": "1.0.0", "status": "ok"}
