"""OdaTrade backtesting engine."""
import pandas as pd
from typing import Callable, Dict, List
from backend.portfolio.pnl import calculate_trade_pnl

class BacktestEngine:
    def __init__(self, initial_balance: float = 5000.0):
        self.balance = initial_balance
        self.trades: List[Dict] = []
        self.equity_curve: List[float] = [initial_balance]

    def run(self, df: pd.DataFrame, signal_fn: Callable) -> Dict:
        position = None
        for i in range(1, len(df)):
            row, prev = df.iloc[i], df.iloc[i - 1]
            signal = signal_fn(row, prev)
            price = row["close"]
            if signal == "BUY" and position is None:
                position = {"entry": price, "qty": self.balance * 0.1 / price}
            elif signal == "SELL" and position:
                pnl = calculate_trade_pnl(position["entry"], price, position["qty"])
                self.balance += pnl["net"]
                self.trades.append({"entry": position["entry"], "exit": price, "pnl": pnl["net"]})
                position = None
            self.equity_curve.append(self.balance)
        return {"trades": len(self.trades), "final_balance": self.balance, "equity": self.equity_curve}
