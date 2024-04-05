"""Backtest performance metrics."""
from backend.portfolio.analytics import sharpe_ratio, max_drawdown, win_rate

def compute_metrics(equity_curve, trade_pnls):
    returns = [(equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1] for i in range(1, len(equity_curve)) if equity_curve[i-1]]
    return {
        "sharpe": sharpe_ratio(returns),
        "max_drawdown": max_drawdown(equity_curve),
        "win_rate": win_rate(trade_pnls),
        "total_trades": len(trade_pnls),
        "total_pnl": sum(trade_pnls),
    }
