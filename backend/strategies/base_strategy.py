# backend/strategy/base_strategy.py

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import pandas as pd


class BaseStrategy(ABC):
    def __init__(self, name: str = "UnnamedStrategy"):
        self.name = name

    @abstractmethod
    def evaluate(
        self, data: Dict[str, pd.DataFrame]
    ) -> Optional[Dict[str, Dict[str, str]]]:
        """
        Evaluate market data for multiple symbols.

        Args:
            data: Dictionary with symbol as key and corresponding DataFrame as value.

        Returns:
            A dictionary like:
            {
                'BTCUSDT': {
                    'action': 'BUY' or 'SELL',
                    'reason': 'some reason',
                    'strategy': 'StrategyName'
                },
                'ETHUSDT': {
                    'action': 'HOLD',
                    'reason': 'No clear signal',
                    'strategy': 'StrategyName'
                },
                ...
            }
            Or None.
        """
        pass
