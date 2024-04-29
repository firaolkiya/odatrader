"""Reject stale market data after gateway disconnect/reconnect."""
import time
from typing import Optional


class StaleQuoteGuard:
    """
    After reconnect, quotes older than the disconnect window or max_age are dropped.
    Prevents signals from firing on cached/stale book data.
    """

    def __init__(self, max_age_sec: float = 5.0, grace_after_reconnect_sec: float = 2.0):
        self.max_age_sec = max_age_sec
        self.grace_after_reconnect_sec = grace_after_reconnect_sec
        self._disconnected_at: Optional[float] = None
        self._reconnected_at: Optional[float] = None
        self.dropped_count = 0

    def on_disconnect(self, ts: Optional[float] = None):
        self._disconnected_at = ts or time.time()
        self._reconnected_at = None

    def on_reconnect(self, ts: Optional[float] = None):
        self._reconnected_at = ts or time.time()

    def is_in_grace_period(self, now_ts: Optional[float] = None) -> bool:
        if self._reconnected_at is None:
            return False
        now = now_ts if now_ts is not None else time.time()
        return (now - self._reconnected_at) < self.grace_after_reconnect_sec

    def accept_quote(self, quote_ts: float, now_ts: Optional[float] = None) -> bool:
        now = now_ts if now_ts is not None else time.time()
        age = now - quote_ts

        if self.is_in_grace_period(now):
            self.dropped_count += 1
            return False

        if age > self.max_age_sec:
            self.dropped_count += 1
            return False

        if self._disconnected_at and quote_ts < self._disconnected_at:
            self.dropped_count += 1
            return False

        return True
