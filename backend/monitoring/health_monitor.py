"""Bot health monitor."""
from datetime import datetime, timezone

class HealthMonitor:
    def __init__(self):
        self.last_heartbeat = None
        self.errors = []

    def heartbeat(self):
        self.last_heartbeat = datetime.now(timezone.utc)

    def record_error(self, error: str):
        self.errors.append({"error": error, "ts": datetime.now(timezone.utc).isoformat()})

    def is_healthy(self) -> bool:
        return self.last_heartbeat is not None and len(self.errors) < 10
