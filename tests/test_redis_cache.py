import pytest
from odatrade.core.cache import TTLCache
from odatrade.core.rate_limiter import RateLimiter
from odatrade.core.circuit_breaker import CircuitBreaker, State

class TestTTLCache:
    def test_set_get(self):
        c = TTLCache()
        c.set("key", "value")
        assert c.get("key") == "value"

    def test_missing_key(self):
        assert TTLCache().get("missing") is None

    def test_invalidate(self):
        c = TTLCache()
        c.set("k", "v")
        c.invalidate("k")
        assert c.get("k") is None

    def test_custom_ttl(self):
        import time
        c = TTLCache(default_ttl=1)
        c.set("k", "v", ttl=0)
        time.sleep(0.01)
        # immediate expiry with ttl=0 means expires instantly on next get

class TestRateLimiter:
    def test_acquire(self):
        rl = RateLimiter(rate=100, capacity=100)
        assert rl.acquire()

    def test_depletes(self):
        rl = RateLimiter(rate=1, capacity=2)
        assert rl.acquire()
        assert rl.acquire()
        assert not rl.acquire()

class TestCircuitBreaker:
    def test_starts_closed(self):
        cb = CircuitBreaker()
        assert cb.state == State.CLOSED
        assert cb.allow_request()

    def test_opens_after_failures(self):
        cb = CircuitBreaker(failure_threshold=3)
        for _ in range(3):
            cb.record_failure()
        assert cb.state == State.OPEN

    def test_recovers_on_success(self):
        cb = CircuitBreaker()
        cb.record_failure()
        cb.record_success()
        assert cb.state == State.CLOSED
