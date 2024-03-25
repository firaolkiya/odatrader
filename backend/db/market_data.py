import pandas as pd
from sqlalchemy import create_engine, text
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config.config import DATABASE_URL

DB_URL = F"{DATABASE_URL}"
engine = create_engine(DB_URL)

def get_latest_prices_df(symbol: str):
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT "timestamp", "open", "high", "low", "close", "volume"
            FROM market_data
            WHERE "symbol" = :symbol
            ORDER BY "timestamp" DESC
            LIMIT 30;
        """), {"symbol": symbol.lower()})
        
        rows = result.fetchall()
        if not rows:
            return pd.DataFrame()  # return empty DataFrame if no data

        # Convert rows to DataFrame
        df = pd.DataFrame(rows, columns=result.keys())
        return df
