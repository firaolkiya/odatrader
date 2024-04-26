"""Grid trading strategy for range-bound markets."""
from typing import Dict, List
from backend.strategies.base_strategy import BaseStrategy


class GridTradingStrategy(BaseStrategy):
    def __init__(self, grid_spacing_pct: float = 0.005, levels: int = 5, size_per_level: float = 0.01):
        super().__init__(name="GridTrading")
        self.grid_spacing_pct = grid_spacing_pct
        self.levels = levels
        self.size_per_level = size_per_level
        self._grid_center = None
        self._active_levels: Dict[float, str] = {}

    def _build_grid(self, center_price: float) -> List[float]:
        levels = []
        for i in range(-self.levels, self.levels + 1):
            if i == 0:
                continue
            levels.append(center_price * (1 + i * self.grid_spacing_pct))
        return sorted(levels)

    def evaluate(self, current, previous=None):
        price = current.get("close", 0)
        if self._grid_center is None:
            self._grid_center = price
            self._active_levels = {lv: "buy" if lv < price else "sell" for lv in self._build_grid(price)}

        for level, side in list(self._active_levels.items()):
            if side == "buy" and price <= level:
                del self._active_levels[level]
                return {"action": "BUY", "reason": f"Grid buy at {level:.4f}"}
            if side == "sell" and price >= level:
                del self._active_levels[level]
                return {"action": "SELL", "reason": f"Grid sell at {level:.4f}"}
        return {"action": "HOLD", "reason": f"Grid active ({len(self._active_levels)} levels)"}
