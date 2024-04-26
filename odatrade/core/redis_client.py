"""Redis connection pool and helpers for OdaTrade."""
import json
import logging
from typing import Any, Optional
from contextlib import contextmanager

logger = logging.getLogger("odatrade.redis")

try:
    import redis
    from redis import Redis, ConnectionPool
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    Redis = None
    ConnectionPool = None


class RedisClient:
    """Singleton Redis client with connection pooling."""

    _instance: Optional["RedisClient"] = None
    _pool: Optional[Any] = None

    def __init__(self, url: str = "redis://localhost:6379/0", max_connections: int = 20):
        self.url = url
        self.max_connections = max_connections
        self._client: Optional[Any] = None
        self._connected = False

    @classmethod
    def get_instance(cls, url: str = "redis://localhost:6379/0") -> "RedisClient":
        if cls._instance is None:
            cls._instance = cls(url)
        return cls._instance

    def connect(self) -> bool:
        if not REDIS_AVAILABLE:
            logger.warning("redis-py not installed; using in-memory fallback")
            return False
        try:
            self._pool = ConnectionPool.from_url(
                self.url, max_connections=self.max_connections, decode_responses=True
            )
            self._client = Redis(connection_pool=self._pool)
            self._client.ping()
            self._connected = True
            logger.info("Redis connected: %s", self.url.split("@")[-1])
            return True
        except Exception as e:
            logger.error("Redis connection failed: %s", e)
            self._connected = False
            return False

    @property
    def client(self) -> Optional[Any]:
        return self._client if self._connected else None

    @property
    def is_connected(self) -> bool:
        return self._connected and self._client is not None

    def get(self, key: str) -> Optional[str]:
        if not self.is_connected:
            return None
        return self._client.get(key)

    def set(self, key: str, value: str, ex: int = None) -> bool:
        if not self.is_connected:
            return False
        return bool(self._client.set(key, value, ex=ex))

    def delete(self, key: str) -> bool:
        if not self.is_connected:
            return False
        return bool(self._client.delete(key))

    def hget(self, name: str, key: str) -> Optional[str]:
        if not self.is_connected:
            return None
        return self._client.hget(name, key)

    def hset(self, name: str, key: str, value: str) -> bool:
        if not self.is_connected:
            return False
        return bool(self._client.hset(name, key, value))

    def hgetall(self, name: str) -> dict:
        if not self.is_connected:
            return {}
        return self._client.hgetall(name) or {}

    def publish(self, channel: str, message: str) -> int:
        if not self.is_connected:
            return 0
        return self._client.publish(channel, message)

    def json_set(self, key: str, data: Any, ex: int = None) -> bool:
        return self.set(key, json.dumps(data, default=str), ex=ex)

    def json_get(self, key: str) -> Optional[Any]:
        raw = self.get(key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    def close(self):
        if self._pool:
            self._pool.disconnect()
        self._connected = False
        self._client = None

    @contextmanager
    def pipeline(self):
        if not self.is_connected:
            yield None
            return
        pipe = self._client.pipeline()
        try:
            yield pipe
            pipe.execute()
        except Exception:
            pipe.reset()
            raise
