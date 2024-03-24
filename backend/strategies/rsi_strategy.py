# backend/strategies/rsi_strategy.py
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from .base_strategy import BaseStrategy

class RSIStrategy(BaseStrategy):
    def __init__(self):
        super().__init__(name="RSI")

    def evaluate(self, row, prev_row=None):
        try:
            rsi = row.get('rsi', None)
            symbol = row.get('symbol')

            if rsi is None or rsi != rsi:  # NaN check
                return None

            # Threshold logic — using 40/60 for moderate signals, 30/70 for stronger ones
            if rsi < 30:
                return {
                    'action': 'BUY',
                    'reason': 'RSI below 30 (strong oversold)',
                    'strategy': self.name,
                    'symbol': symbol
                }
            elif rsi > 70:
                return {
                    'action': 'SELL',
                    'reason': 'RSI above 70 (strong overbought)',
                    'strategy': self.name,
                    'symbol': symbol
                }

            # Cross detection (optional)
            if prev_row:
                prev_rsi = prev_row.get('rsi', None)
                if prev_rsi is not None and prev_rsi == prev_rsi:
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
