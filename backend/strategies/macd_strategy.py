# backend/strategies/macd_strategy.py

import pandas as pd
from .base_strategy import BaseStrategy

class MACDStrategy(BaseStrategy):
    def __init__(self):
        super().__init__(name="MACD")

    def evaluate(self, row, prev_row=None):
        try:
            macd = row.get('macd')
            signal = row.get('macd_signal')
            symbol = row.get('symbol')

            # Ensure values are not missing or NaN
            if macd is None or signal is None or pd.isna(macd) or pd.isna(signal):
                return None

            # If accidentally a Series, get last value
            if isinstance(macd, pd.Series):
                macd = macd.iloc[-1]
            if isinstance(signal, pd.Series):
                signal = signal.iloc[-1]

            # MACD crossover logic
            if macd > signal:
                return {
                    'action': 'BUY',
                    'reason': 'MACD crossed above signal line',
                    'strategy': self.name,
                    'symbol': symbol
                }
            elif macd < signal:
                return {
                    'action': 'SELL',
                    'reason': 'MACD crossed below signal line',
                    'strategy': self.name,
                    'symbol': symbol
                }

        except KeyError as e:
            print(f"[{self.name} Strategy Error] Missing column: {e}")
        except Exception as e:
            print(f"[{self.name} Strategy Error] {e}")

        return None
