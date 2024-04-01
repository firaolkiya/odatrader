"""Alert configuration API."""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/alerts", tags=["alerts"])

class AlertRule(BaseModel):
    name: str
    condition: str
    channel: str = "webhook"

@router.get("/")
def list_alerts():
    return {"rules": []}

@router.post("/")
def create_alert(rule: AlertRule):
    return {"created": rule.name}
