"""Token bucket rate limiter."""
import time

class RateLimiter:
    def __init__(self, rate: float = 10.0, capacity: float = 20.0):
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last = time.time()

    def acquire(self, tokens: float = 1.0) -> bool:
        now = time.time()
        self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)
        self.last = now
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
