"""Symbol watchlist manager."""
from typing import List

class SymbolManager:
    def __init__(self, symbols: List[str] = None):
        self._symbols = [s.lower() for s in (symbols or [])]
        self._watchlist = set(self._symbols)

    def add(self, symbol: str):
        self._watchlist.add(symbol.lower())

    def remove(self, symbol: str):
        self._watchlist.discard(symbol.lower())

    def list_all(self) -> List[str]:
        return sorted(self._watchlist)

    def is_watched(self, symbol: str) -> bool:
        return symbol.lower() in self._watchlist
