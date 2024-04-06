"""Historical OHLCV data loader."""
import pandas as pd
from typing import Optional

def load_from_db(engine, symbol: str, limit: int = 1000) -> pd.DataFrame:
    query = f"SELECT * FROM market_data WHERE symbol = '{symbol}' ORDER BY timestamp DESC LIMIT {limit}"
    df = pd.read_sql(query, engine)
    return df.sort_values("timestamp") if not df.empty else df

def load_from_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["timestamp"])
    return df.sort_values("timestamp")
