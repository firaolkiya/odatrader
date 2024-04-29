"""Event deduplication to prevent double-processing in the async pipeline."""
import time
from typing import Dict, Optional, Tuple

from odatrade.core.event_bus_async import Event, EventType


_DEDUP_TYPES = frozenset({
    EventType.STRATEGY_SIGNAL,
    EventType.RISK_APPROVED,
    EventType.ORDER_CREATED,
    EventType.ORDER_FILLED,
})


class EventDeduplicator:
    """Tracks processed events by (bot_id, type, correlation_id, dedupe_key)."""

    def __init__(self, ttl_sec: float = 600.0):
        self.ttl_sec = ttl_sec
        self._seen: Dict[str, float] = {}

    def _purge(self, now: float):
        expired = [k for k, ts in self._seen.items() if now - ts > self.ttl_sec]
        for k in expired:
            del self._seen[k]

    def make_key(self, event: Event, dedupe_key: Optional[str] = None) -> Optional[str]:
        if event.type not in _DEDUP_TYPES:
            return None
        if not event.correlation_id:
            return None
        extra = dedupe_key or event.payload.get("dedupe_key", "")
        return f"{event.bot_id}:{event.type.value}:{event.correlation_id}:{extra}"

    def is_duplicate(self, event: Event, dedupe_key: Optional[str] = None) -> bool:
        key = self.make_key(event, dedupe_key)
        if not key:
            return False
        self._purge(time.time())
        return key in self._seen

    def mark(self, event: Event, dedupe_key: Optional[str] = None) -> Optional[str]:
        key = self.make_key(event, dedupe_key)
        if key:
            self._seen[key] = time.time()
        return key
