"""TTL cache for market data and computed features."""
import time
from typing import Any, Optional

class TTLCache:
    def __init__(self, default_ttl: int = 60):
        self._store = {}
        self._ttl = default_ttl

    def set(self, key: str, value: Any, ttl: int = None):
        self._store[key] = (value, time.time() + (ttl or self._ttl))

    def get(self, key: str) -> Optional[Any]:
        item = self._store.get(key)
        if not item:
            return None
        value, expires = item
        if time.time() > expires:
            del self._store[key]
            return None
        return value

    def invalidate(self, key: str):
        self._store.pop(key, None)
