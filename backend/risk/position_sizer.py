"""Position sizing algorithms."""

def fixed_fraction(balance: float, risk_pct: float, stop_distance: float) -> float:
    if stop_distance <= 0:
        return 0.0
    risk_amount = balance * risk_pct
    return risk_amount / stop_distance

def kelly_criterion(win_rate: float, avg_win: float, avg_loss: float) -> float:
    if avg_loss == 0:
        return 0.0
    b = avg_win / abs(avg_loss)
    f = (win_rate * b - (1 - win_rate)) / b
    return max(0.0, min(f, 0.25))
