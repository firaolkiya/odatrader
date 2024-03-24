# backend/strategies/bb_strategy.py

from .base_strategy import BaseStrategy
import pandas as pd

class BollingerBandsStrategy(BaseStrategy):
    def __init__(self):
        super().__init__(name="Bollinger_Bands")

    def evaluate(self, row: dict, prev_row: dict = None):
        try:
            bb_upper = row.get('bb_upper')
            bb_lower = row.get('bb_lower')
            close = row.get('close')
            symbol = row.get('symbol')

            # Ensure scalar (not Series) values
            if any(pd.isna(val) for val in [bb_upper, bb_lower, close]):
                return None

            # Reversion Buy Signal
            if prev_row:
                prev_close = prev_row.get('close')
                prev_bb_lower = prev_row.get('bb_lower')
                prev_bb_upper = prev_row.get('bb_upper')

                if any(pd.isna(val) for val in [prev_close, prev_bb_lower, prev_bb_upper]):
                    return None

                if close > bb_lower and prev_close < prev_bb_lower:
                    return {
                        'action': 'BUY',
                        'reason': 'Price bounced above lower Bollinger Band (reversion)',
                        'strategy': self.name,
                        'symbol': symbol
                    }

                elif close < bb_upper and prev_close > prev_bb_upper:
                    return {
                        'action': 'SELL',
                        'reason': 'Price dropped below upper Bollinger Band (reversion)',
                        'strategy': self.name,
                        'symbol': symbol
                    }

        except Exception as e:
            print(f"[{self.name} Error] {e}")

        return None
