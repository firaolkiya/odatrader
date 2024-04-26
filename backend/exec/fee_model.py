"""Maker/taker fee model for realistic cost simulation."""

class FeeModel:
    DEFAULT_MAKER = 0.0002
    DEFAULT_TAKER = 0.00075

    def __init__(self, maker_rate: float = None, taker_rate: float = None, venue: str = "binance"):
        self.maker_rate = maker_rate or self.DEFAULT_MAKER
        self.taker_rate = taker_rate or self.DEFAULT_TAKER
        self.venue = venue
        self._rebates_collected = 0.0

    def compute(self, price: float, quantity: float, maker: bool = False) -> float:
        rate = self.maker_rate if maker else self.taker_rate
        notional = price * quantity
        fee = notional * abs(rate)
        if maker and rate < 0:
            self._rebates_collected += abs(fee)
        return fee

    def cost_per_trade(self, maker: bool = False) -> float:
        return self.maker_rate if maker else self.taker_rate

    @property
    def rebates(self) -> float:
        return self._rebates_collected
