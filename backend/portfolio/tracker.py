"""Portfolio position tracker."""
from typing import Dict
from dataclasses import dataclass, field

@dataclass
class Position:
    symbol: str
    quantity: float = 0.0
    avg_entry: float = 0.0
    unrealized_pnl: float = 0.0

class PortfolioTracker:
    def __init__(self, starting_balance: float = 5000.0):
        self.balance = starting_balance
        self.positions: Dict[str, Position] = {}

    def update_position(self, symbol: str, qty: float, price: float):
        pos = self.positions.get(symbol, Position(symbol=symbol))
        if qty > 0:
            total_cost = pos.avg_entry * pos.quantity + price * qty
            pos.quantity += qty
            pos.avg_entry = total_cost / pos.quantity if pos.quantity else 0
        else:
            pos.quantity += qty
        self.positions[symbol] = pos

    def get_summary(self):
        return {"balance": self.balance, "positions": len(self.positions), "equity": self.balance}

    def get_positions(self):
        return {k: {"qty": v.quantity, "entry": v.avg_entry, "pnl": v.unrealized_pnl} for k, v in self.positions.items()}
