"""Event-driven replay backtester using same engine logic as live trading."""
import logging
from typing import Callable, List
import pandas as pd
from backend.engine.adaptive_voter import AdaptiveVoter
from backend.backtesting.engine import BacktestEngine
from backend.exec.fee_model import FeeModel
from backend.exec.slippage import SlippageModel

logger = logging.getLogger("odatrade.replay")


class ReplayBacktester:
    """Replays historical bars through adaptive voter + execution simulation."""

    def __init__(self, symbol: str, initial_balance: float = 5000.0, config: dict = None):
        self.symbol = symbol
        self.voter = AdaptiveVoter(symbol, config)
        self.engine = BacktestEngine(initial_balance)
        self.fee_model = FeeModel()
        self.slippage = SlippageModel()
        self.trades: List[dict] = []

    def run(self, df: pd.DataFrame) -> dict:
        position = None
        for i in range(30, len(df)):
            window = df.iloc[max(0, i - 100):i + 1]
            snap = self.voter.evaluate(window)
            price = df.iloc[i]["close"]
            if snap.action == "BUY" and position is None:
                fill = self.slippage.apply(price, 1.0, side="buy")
                position = {"entry": fill, "qty": self.engine.balance * 0.1 / fill}
            elif snap.action == "SELL" and position:
                fill = self.slippage.apply(price, position["qty"], side="sell")
                gross = (fill - position["entry"]) * position["qty"]
                fees = self.fee_model.compute(position["entry"], position["qty"]) + self.fee_model.compute(fill, position["qty"])
                net = gross - fees
                self.engine.balance += net
                self.trades.append({"entry": position["entry"], "exit": fill, "pnl": net, "regime": snap.regime})
                position = None
            self.engine.equity_curve.append(self.engine.balance)
        return {
            "trades": len(self.trades), "final_balance": self.engine.balance,
            "trade_details": self.trades, "equity": self.engine.equity_curve,
        }
