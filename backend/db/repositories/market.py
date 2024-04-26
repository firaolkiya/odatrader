"""Market data repository."""
from typing import List, Optional
from sqlalchemy import text
import pandas as pd


class MarketDataRepository:
    def __init__(self, pool):
        self.pool = pool

    def ensure_table(self):
        with self.pool.connection() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS market_data (
                    symbol TEXT NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL,
                    open FLOAT, high FLOAT, low FLOAT, close FLOAT, volume FLOAT,
                    bot_id TEXT DEFAULT 'default',
                    PRIMARY KEY (symbol, timestamp)
                )
            """))

    def insert_candle(self, symbol: str, candle: dict, bot_id: str = "default"):
        with self.pool.connection() as conn:
            conn.execute(text("""
                INSERT INTO market_data (symbol, timestamp, open, high, low, close, volume, bot_id)
                VALUES (:symbol, to_timestamp(:ts / 1000.0), :open, :high, :low, :close, :volume, :bot_id)
                ON CONFLICT (symbol, timestamp) DO NOTHING
            """), {
                "symbol": symbol, "ts": candle.get("t", 0),
                "open": float(candle.get("o", 0)), "high": float(candle.get("h", 0)),
                "low": float(candle.get("l", 0)), "close": float(candle.get("c", 0)),
                "volume": float(candle.get("v", 0)), "bot_id": bot_id,
            })

    def get_candles(self, symbol: str, limit: int = 100) -> pd.DataFrame:
        with self.pool.connection() as conn:
            df = pd.read_sql(text(
                "SELECT * FROM market_data WHERE symbol = :symbol ORDER BY timestamp DESC LIMIT :limit"
            ), conn, params={"symbol": symbol, "limit": limit})
        return df.sort_values("timestamp") if not df.empty else df
