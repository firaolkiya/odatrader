"""Audit log for bot actions."""
from datetime import datetime, timezone

class AuditLog:
    def __init__(self):
        self.events = []

    def record(self, action: str, actor: str = "system", details: dict = None):
        self.events.append({
            "action": action, "actor": actor, "details": details or {},
            "ts": datetime.now(timezone.utc).isoformat(),
        })

    def recent(self, limit: int = 50):
        return self.events[-limit:]
