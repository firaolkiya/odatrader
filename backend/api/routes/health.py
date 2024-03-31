"""Health check routes."""
from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
def health():
    return {"status": "healthy", "service": "OdaTrade", "ts": datetime.now(timezone.utc).isoformat()}

@router.get("/ready")
def readiness():
    return {"ready": True}
