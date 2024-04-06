"""Multi-symbol market scanner."""
from typing import List, Dict
import pandas as pd

class MarketScanner:
    def __init__(self, symbols: List[str]):
        self.symbols = symbols

    def scan_rsi(self, data: Dict[str, pd.DataFrame], oversold: float = 30, overbought: float = 70) -> List[Dict]:
        results = []
        for symbol, df in data.items():
            if df.empty or "rsi" not in df.columns:
                continue
            rsi = df["rsi"].iloc[-1]
            if rsi < oversold:
                results.append({"symbol": symbol, "signal": "BUY", "rsi": rsi})
            elif rsi > overbought:
                results.append({"symbol": symbol, "signal": "SELL", "rsi": rsi})
        return results
