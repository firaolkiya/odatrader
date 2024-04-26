"""Trade repository for PostgreSQL."""
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import text


class TradeRepository:
    def __init__(self, pool):
        self.pool = pool

    def ensure_table(self):
        with self.pool.connection() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS trades (
                    id SERIAL PRIMARY KEY,
                    bot_id TEXT,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    price FLOAT NOT NULL,
                    quantity FLOAT NOT NULL,
                    pnl FLOAT DEFAULT 0,
                    strategy TEXT,
                    timestamp TIMESTAMPTZ DEFAULT NOW()
                )
            """))

    def insert(self, bot_id: str, symbol: str, side: str, price: float, quantity: float,
               pnl: float = 0, strategy: str = "") -> int:
        with self.pool.connection() as conn:
            result = conn.execute(text("""
                INSERT INTO trades (bot_id, symbol, side, price, quantity, pnl, strategy, timestamp)
                VALUES (:bot_id, :symbol, :side, :price, :qty, :pnl, :strategy, :ts)
                RETURNING id
            """), {
                "bot_id": bot_id, "symbol": symbol, "side": side,
                "price": price, "qty": quantity, "pnl": pnl,
                "strategy": strategy, "ts": datetime.now(timezone.utc),
            })
            return result.scalar()

    def list_trades(self, bot_id: str = None, symbol: str = None, limit: int = 50) -> List[dict]:
        query = "SELECT * FROM trades WHERE 1=1"
        params = {"limit": limit}
        if bot_id:
            query += " AND bot_id = :bot_id"
            params["bot_id"] = bot_id
        if symbol:
            query += " AND symbol = :symbol"
            params["symbol"] = symbol
        query += " ORDER BY timestamp DESC LIMIT :limit"
        with self.pool.connection() as conn:
            rows = conn.execute(text(query), params).fetchall()
            return [dict(row._mapping) for row in rows]

    def stats(self, bot_id: str = None) -> dict:
        query = """
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
                   SUM(pnl) as total_pnl,
                   AVG(pnl) as avg_pnl
            FROM trades
        """
        params = {}
        if bot_id:
            query += " WHERE bot_id = :bot_id"
            params["bot_id"] = bot_id
        with self.pool.connection() as conn:
            row = conn.execute(text(query), params).fetchone()
            total = row.total or 0
            wins = row.wins or 0
            return {
                "total": total,
                "wins": wins,
                "losses": total - wins,
                "win_rate": wins / total if total else 0,
                "total_pnl": float(row.total_pnl or 0),
                "avg_pnl": float(row.avg_pnl or 0),
            }
