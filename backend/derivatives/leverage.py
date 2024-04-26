"""Leverage-aware position sizing (Milestone 3)."""
import logging

logger = logging.getLogger("odatrade.leverage")


def volatility_aware_size(
    equity: float,
    risk_pct: float,
    atr: float,
    sl_atr_mult: float,
    price: float,
    max_leverage: float = 5.0,
    contract_size: float = 1.0,
    margin_factor: float = 0.1,
) -> dict:
    risk_amount = equity * risk_pct
    stop_distance = atr * sl_atr_mult
    if stop_distance <= 0 or price <= 0:
        return {"size": 0, "notional": 0, "leverage": 0}
    position_notional = risk_amount / (stop_distance / price)
    max_lev = min(max_leverage, position_notional / (equity * margin_factor)) if equity > 0 else 1
    size = int(position_notional / (price * contract_size))
    return {
        "size": max(0, size),
        "notional": position_notional,
        "leverage": max_lev,
        "stop_distance": stop_distance,
        "risk_amount": risk_amount,
    }


class LeverageManager:
    def __init__(self, max_global_leverage: float = 5.0, max_per_instrument: float = 3.0):
        self.max_global_leverage = max_global_leverage
        self.max_per_instrument = max_per_instrument
        self._positions: dict = {}

    def check_leverage(self, symbol: str, notional: float, equity: float) -> tuple:
        if equity <= 0:
            return False, "zero equity"
        lev = notional / equity
        if lev > self.max_per_instrument:
            return False, f"per-instrument leverage {lev:.1f}x > {self.max_per_instrument}x"
        total_notional = sum(self._positions.values()) + notional
        global_lev = total_notional / equity
        if global_lev > self.max_global_leverage:
            return False, f"global leverage {global_lev:.1f}x > {self.max_global_leverage}x"
        return True, "ok"

    def update_position(self, symbol: str, notional: float):
        self._positions[symbol] = notional
