"""Value-at-Risk calculator."""
import math
from typing import List

def historical_var(returns: List[float], confidence: float = 0.95) -> float:
    if not returns:
        return 0.0
    sorted_r = sorted(returns)
    idx = int((1 - confidence) * len(sorted_r))
    return abs(sorted_r[idx])

def parametric_var(returns: List[float], confidence: float = 0.95) -> float:
    if len(returns) < 2:
        return 0.0
    mean = sum(returns) / len(returns)
    var = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)
    z = 1.645 if confidence == 0.95 else 2.326
    return abs(mean - z * math.sqrt(var))
