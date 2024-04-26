"""Funding rate filter for perpetual futures."""

class FundingRateFilter:
    def __init__(self, max_funding: float = 0.001, skip_negative_threshold: float = -0.0005):
        self.max_funding = max_funding
        self.skip_negative_threshold = skip_negative_threshold

    def should_trade(self, funding_rate: float, side: str, holding_hours: float = 8.0) -> tuple:
        expected_cost = funding_rate * holding_hours / 8
        if side == "long" and funding_rate > self.max_funding:
            return False, f"funding too high for long: {funding_rate:.4%}"
        if side == "short" and funding_rate < self.skip_negative_threshold:
            return False, f"funding too negative for short: {funding_rate:.4%}"
        return True, f"expected funding cost: {expected_cost:.4%}"

    def adjust_expected_pnl(self, trade_pnl: float, funding_rate: float, notional: float, hours: float) -> float:
        funding_cost = funding_rate * notional * (hours / 8)
        return trade_pnl - funding_cost
