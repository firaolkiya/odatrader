"""Portfolio analytics engine."""
import math
from typing import List

def sharpe_ratio(returns: List[float], risk_free: float = 0.0) -> float:
    if len(returns) < 2:
        return 0.0
    excess = [r - risk_free for r in returns]
    mean = sum(excess) / len(excess)
    var = sum((r - mean) ** 2 for r in excess) / (len(excess) - 1)
    std = math.sqrt(var) if var > 0 else 0
    return mean / std * math.sqrt(252) if std else 0.0

def max_drawdown(equity_curve: List[float]) -> float:
    peak = equity_curve[0] if equity_curve else 0
    max_dd = 0.0
    for v in equity_curve:
        peak = max(peak, v)
        dd = (peak - v) / peak if peak else 0
        max_dd = max(max_dd, dd)
    return max_dd

def win_rate(pnls: List[float]) -> float:
    if not pnls:
        return 0.0
    return sum(1 for p in pnls if p > 0) / len(pnls)
