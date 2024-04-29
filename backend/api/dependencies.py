"""Shared FastAPI dependencies for OdaTrade."""
import os
from functools import lru_cache
from typing import Optional

from backend.db.postgres_pool import PostgresPool
from odatrade.core.redis_client import RedisClient
from odatrade.core.redis_state import RedisStateStore


@lru_cache()
def get_redis_client() -> RedisClient:
    url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    client = RedisClient.get_instance(url)
    if not client.is_connected:
        client.connect()
    return client


@lru_cache()
def get_postgres_pool() -> Optional[PostgresPool]:
    url = os.getenv("DATABASE_URL", "")
    if not url or "postgresql" not in url:
        return None
    pool = PostgresPool(url)
    pool.connect()
    return pool


def get_state_store() -> RedisStateStore:
    return RedisStateStore(get_redis_client())


def get_db_session():
    pool = get_postgres_pool()
    if not pool:
        raise RuntimeError("PostgreSQL not configured")
    with pool.session() as session:
        yield session
