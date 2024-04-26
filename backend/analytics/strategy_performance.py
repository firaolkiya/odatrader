"""Per-strategy performance tracker."""
from collections import defaultdict

class StrategyPerformanceTracker:
    def __init__(self):
        self.stats = defaultdict(lambda: {"wins": 0, "losses": 0, "pnl": 0.0})

    def record(self, strategy: str, pnl: float):
        s = self.stats[strategy]
        s["pnl"] += pnl
        if pnl > 0:
            s["wins"] += 1
        else:
            s["losses"] += 1

    def get_stats(self, strategy: str = None):
        if strategy:
            return dict(self.stats[strategy])
        return {k: dict(v) for k, v in self.stats.items()}
