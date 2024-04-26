"""Strategy signal repository."""
from datetime import datetime, timezone
from typing import List
from sqlalchemy import text


class SignalRepository:
    def __init__(self, pool):
        self.pool = pool

    def ensure_table(self):
        with self.pool.connection() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS strategy_signals (
                    id SERIAL PRIMARY KEY,
                    bot_id TEXT,
                    symbol TEXT NOT NULL,
                    strategy TEXT NOT NULL,
                    action TEXT NOT NULL,
                    reason TEXT DEFAULT '',
                    executed BOOLEAN DEFAULT FALSE,
                    timestamp TIMESTAMPTZ DEFAULT NOW()
                )
            """))

    def insert(self, bot_id: str, symbol: str, strategy: str, action: str, reason: str = "") -> int:
        with self.pool.connection() as conn:
            result = conn.execute(text("""
                INSERT INTO strategy_signals (bot_id, symbol, strategy, action, reason, timestamp)
                VALUES (:bot_id, :symbol, :strategy, :action, :reason, :ts)
                RETURNING id
            """), {
                "bot_id": bot_id, "symbol": symbol, "strategy": strategy,
                "action": action, "reason": reason,
                "ts": datetime.now(timezone.utc),
            })
            return result.scalar()

    def recent(self, bot_id: str = None, limit: int = 100) -> List[dict]:
        query = "SELECT * FROM strategy_signals"
        params = {"limit": limit}
        if bot_id:
            query += " WHERE bot_id = :bot_id"
            params["bot_id"] = bot_id
        query += " ORDER BY timestamp DESC LIMIT :limit"
        with self.pool.connection() as conn:
            rows = conn.execute(text(query), params).fetchall()
            return [dict(row._mapping) for row in rows]
