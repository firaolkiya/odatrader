"""Monte Carlo bootstrapping of trade sequences for tail risk analysis."""
import random
import math
from typing import List, Dict


class MonteCarloSimulator:
    def __init__(self, n_simulations: int = 1000):
        self.n_simulations = n_simulations

    def run(self, trade_pnls: List[float], initial_balance: float = 5000.0) -> Dict:
        if not trade_pnls:
            return {"error": "no trades"}
        final_balances = []
        max_drawdowns = []
        for _ in range(self.n_simulations):
            shuffled = random.choices(trade_pnls, k=len(trade_pnls))
            balance = initial_balance
            peak = balance
            max_dd = 0.0
            for pnl in shuffled:
                balance += pnl
                peak = max(peak, balance)
                dd = (peak - balance) / peak if peak else 0
                max_dd = max(max_dd, dd)
            final_balances.append(balance)
            max_drawdowns.append(max_dd)
        final_balances.sort()
        return {
            "n_simulations": self.n_simulations,
            "median_final": final_balances[len(final_balances) // 2],
            "p5_final": final_balances[int(len(final_balances) * 0.05)],
            "p95_final": final_balances[int(len(final_balances) * 0.95)],
            "median_max_dd": sorted(max_drawdowns)[len(max_drawdowns) // 2],
            "worst_max_dd": max(max_drawdowns),
            "prob_profit": sum(1 for b in final_balances if b > initial_balance) / len(final_balances),
        }
