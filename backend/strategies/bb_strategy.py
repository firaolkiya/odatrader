# backend/strategies/bollinger_strategy.py
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from .base_strategy import BaseStrategy

class BollingerStrategy(BaseStrategy):
    def __init__(self):
        super().__init__(name="Bollinger")

    def evaluate(self, row, prev_row=None):
        try:
            close = float(row['close']) if 'close' in row and row['close'] == row['close'] else None
            bb_upper = float(row['bb_upper']) if 'bb_upper' in row and row['bb_upper'] == row['bb_upper'] else None
            bb_lower = float(row['bb_lower']) if 'bb_lower' in row and row['bb_lower'] == row['bb_lower'] else None
            symbol = row['symbol'] if 'symbol' in row else None

            if close is None or bb_upper is None or bb_lower is None:
                return None

            # Mean Reversion Buy: price bounces above lower band
            if prev_row is not None:
                prev_close = float(prev_row['close']) if 'close' in prev_row and prev_row['close'] == prev_row['close'] else None
                prev_bb_lower = float(prev_row['bb_lower']) if 'bb_lower' in prev_row and prev_row['bb_lower'] == prev_row['bb_lower'] else None
                prev_bb_upper = float(prev_row['bb_upper']) if 'bb_upper' in prev_row and prev_row['bb_upper'] == prev_row['bb_upper'] else None

                if prev_close is not None and prev_bb_lower is not None and close > bb_lower and prev_close < prev_bb_lower:
                    return {
                        'action': 'BUY',
                        'reason': 'Price bounced above lower Bollinger Band (reversion)',
                        'strategy': self.name,
                        'symbol': symbol
                    }

                # Mean Reversion Sell: price drops below upper band
                if prev_close is not None and prev_bb_upper is not None and close < bb_upper and prev_close > prev_bb_upper:
                    return {
                        'action': 'SELL',
                        'reason': 'Price dropped below upper Bollinger Band (reversion)',
                        'strategy': self.name,
                        'symbol': symbol
                    }

        except Exception as e:
            print(f"[{self.name} Strategy Error] {e}")

        return None
