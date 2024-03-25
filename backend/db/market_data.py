from sqlalchemy import create_engine, text
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config.config import DATABASE_URL

DB_URL = F"{DATABASE_URL}"
engine = create_engine(DB_URL)

def get_latest_price(symbol: str):
    with engine.connect() as conn:
        result = conn.execute(text(f"""
            SELECT "close", "timestamp"
            FROM market_data
            WHERE "symbol" = :symbol
            ORDER BY "timestamp" DESC
            LIMIT 1;
        """), {"symbol": symbol.lower()})
        row = result.fetchone()
        return {"price": row[0], "timestamp": row[1]} if row else None
