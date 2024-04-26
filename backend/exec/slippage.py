"""Slippage model for backtesting and paper trading."""

class SlippageModel:
    def __init__(self, base_slippage_bps: float = 5.0, impact_factor: float = 0.0001):
        self.base_slippage_bps = base_slippage_bps
        self.impact_factor = impact_factor

    def apply(self, price: float, quantity: float, side: str = "buy", avg_volume: float = 1e6) -> float:
        base = price * (self.base_slippage_bps / 10000)
        impact = price * self.impact_factor * (quantity / max(avg_volume * 0.01, 1))
        slip = base + impact
        if side == "buy":
            return price + slip
        return price - slip

    def simulate_fill(self, price: float, quantity: float, bids: list, asks: list, side: str) -> tuple:
        """Simulate fill against orderbook depth."""
        book = asks if side == "buy" else bids
        remaining = quantity
        total_cost = 0.0
        for px, qty in book:
            fill_qty = min(remaining, qty)
            total_cost += fill_qty * px
            remaining -= fill_qty
            if remaining <= 0:
                break
        if remaining > 0:
            worst_px = book[-1][0] if book else price
            total_cost += remaining * worst_px * 1.001
        avg_px = total_cost / quantity if quantity else price
        return avg_px, quantity - max(0, remaining)
