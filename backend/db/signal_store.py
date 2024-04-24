"""Signal history persistence."""
from datetime import datetime, timezone
from sqlalchemy import text

class SignalStore:
    def __init__(self, engine):
        self.engine = engine

    def save(self, symbol: str, strategy: str, action: str, reason: str = ""):
        with self.engine.begin() as conn:
            conn.execute(text(
                "INSERT INTO strategy_signals (symbol, strategy, action, timestamp, reason, executed) "
                "VALUES (:s, :st, :a, :t, :r, false)"
            ), {"s": symbol, "st": strategy, "a": action, "t": datetime.now(timezone.utc), "r": reason})
