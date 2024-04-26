"""Orderbook-depth slippage model for realistic backtesting."""
from backend.exec.slippage import SlippageModel


class BacktestSlippageModel(SlippageModel):
    def model_from_volume(self, price: float, quantity: float, daily_volume: float) -> float:
        participation = quantity / max(daily_volume * 0.01, 1)
        return self.apply(price, quantity, avg_volume=daily_volume) * (1 + participation)
