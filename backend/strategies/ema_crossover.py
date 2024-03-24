# backend/strategies/ema_crossover.py
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from .base_strategy import BaseStrategy
import pandas as pd

class EMACrossoverStrategy(BaseStrategy):
    def __init__(self):
        super().__init__(name="EMA_Crossover")

    def evaluate(self, row, prev_row=None):
        try:
            fast = row.get('ema_fast')
            slow = row.get('ema_slow')
            symbol = row.get('symbol')

            # Ensure values are not missing or NaN
            if fast is None or slow is None or pd.isna(fast) or pd.isna(slow):
                return None

            # Convert to scalar if accidentally a Series
            if isinstance(fast, pd.Series):
                fast = fast.iloc[-1]
            if isinstance(slow, pd.Series):
                slow = slow.iloc[-1]

            if fast > slow:
                return {
                    'action': 'BUY',
                    'reason': 'EMA fast crossed above EMA slow',
                    'strategy': self.name,
                    'symbol': symbol
                }
            elif fast < slow:
                return {
                    'action': 'SELL',
                    'reason': 'EMA fast crossed below EMA slow',
                    'strategy': self.name,
                    'symbol': symbol
                }

        except Exception as e:
            print(f"[{self.name} Error] {e}")

        return None
