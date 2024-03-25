# backend/strategies/rsi_strategy.py
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from .base_strategy import BaseStrategy

class RSIStrategy(BaseStrategy):
    def __init__(self):
        super().__init__(name="RSI")

    def evaluate(self, row, prev_row=None):
        try:
            # Safely extract values
            rsi = float(row['rsi']) if 'rsi' in row and row['rsi'] == row['rsi'] else None
            symbol = row['symbol'] if 'symbol' in row else None

            if rsi is None:
                return None

            # Main RSI signals
            if rsi < 45:
                return {
                    'action': 'BUY',
                    'reason': 'RSI below 30 (strong oversold)',
                    'strategy': self.name,
                    'symbol': symbol
                }
            elif rsi > 60:
                return {
                    'action': 'SELL',
                    'reason': 'RSI above 70 (strong overbought)',
                    'strategy': self.name,
                    'symbol': symbol
                }

            # Cross logic
            if prev_row is not None and 'rsi' in prev_row:
                prev_rsi = float(prev_row['rsi']) if prev_row['rsi'] == prev_row['rsi'] else None
                if prev_rsi is not None:
                    if prev_rsi > 30 and rsi < 30:
                        return {
                            'action': 'BUY',
                            'reason': 'RSI just crossed below 30',
                            'strategy': self.name,
                            'symbol': symbol
                        }
                    elif prev_rsi < 70 and rsi > 70:
                        return {
                            'action': 'SELL',
                            'reason': 'RSI just crossed above 70',
                            'strategy': self.name,
                            'symbol': symbol
                        }

        except Exception as e:
            print(f"[{self.name} Strategy Error] {e}")

        return None
