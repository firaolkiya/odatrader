"""PostgreSQL connection pool with health checks and retry logic."""
import logging
import time
from contextlib import contextmanager
from typing import Optional, Generator

from sqlalchemy import create_engine, text, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

logger = logging.getLogger("odatrade.postgres")


class PostgresPool:
    """Managed PostgreSQL connection pool for OdaTrade."""

    def __init__(
        self,
        database_url: str,
        pool_size: int = 10,
        max_overflow: int = 20,
        pool_timeout: int = 30,
        pool_recycle: int = 1800,
        echo: bool = False,
    ):
        self.database_url = database_url
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self._engine: Optional[Engine] = None
        self._session_factory = None
        self._connected = False
        self._retry_attempts = 3
        self._retry_delay = 1.0

    def connect(self) -> bool:
        for attempt in range(self._retry_attempts):
            try:
                self._engine = create_engine(
                    self.database_url,
                    poolclass=QueuePool,
                    pool_size=self.pool_size,
                    max_overflow=self.max_overflow,
                    pool_timeout=30,
                    pool_recycle=1800,
                    pool_pre_ping=True,
                )
                self._session_factory = sessionmaker(bind=self._engine)
                with self._engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                self._connected = True
                logger.info("PostgreSQL pool connected (size=%d)", self.pool_size)
                return True
            except Exception as e:
                logger.warning("PostgreSQL connect attempt %d failed: %s", attempt + 1, e)
                time.sleep(self._retry_delay * (attempt + 1))
        self._connected = False
        return False

    @property
    def engine(self) -> Optional[Engine]:
        return self._engine

    @property
    def is_connected(self) -> bool:
        return self._connected and self._engine is not None

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        if not self.is_connected:
            raise ConnectionError("PostgreSQL pool not connected")
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @contextmanager
    def connection(self):
        if not self.is_connected:
            raise ConnectionError("PostgreSQL pool not connected")
        conn = self._engine.connect()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def health_check(self) -> dict:
        if not self.is_connected:
            return {"status": "disconnected", "pool_size": 0}
        try:
            start = time.time()
            with self.connection() as conn:
                conn.execute(text("SELECT 1"))
            latency = (time.time() - start) * 1000
            pool = self._engine.pool
            return {
                "status": "healthy",
                "latency_ms": round(latency, 2),
                "pool_size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def init_tables(self):
        from backend.db.models import Base
        from backend.db.migrations import run_migrations
        Base.metadata.create_all(self._engine)
        run_migrations(self._engine)
        logger.info("Database tables initialized")

    def close(self):
        if self._engine:
            self._engine.dispose()
        self._connected = False
