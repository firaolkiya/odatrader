"""Trade journal with notes."""
from datetime import datetime, timezone
from typing import List, Dict

class TradeJournal:
    def __init__(self):
        self.entries: List[Dict] = []

    def add(self, trade_id: str, symbol: str, note: str, tags: List[str] = None):
        self.entries.append({
            "trade_id": trade_id, "symbol": symbol, "note": note,
            "tags": tags or [], "created_at": datetime.now(timezone.utc).isoformat(),
        })

    def search(self, symbol: str = None) -> List[Dict]:
        if symbol:
            return [e for e in self.entries if e["symbol"] == symbol]
        return self.entries
