"""PnL calculator with fee modeling."""
from odatrade.core.constants import FEE_RATE

def calculate_trade_pnl(entry: float, exit: float, qty: float, side: str = "long") -> dict:
    gross = (exit - entry) * qty if side == "long" else (entry - exit) * qty
    fees = (entry + exit) * qty * FEE_RATE
    net = gross - fees
    return {"gross": gross, "fees": fees, "net": net, "return_pct": net / (entry * qty) if entry * qty else 0}
