import os
import sys
from typing import Dict, List
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.strategies.rsi_strategy import RSIStrategy
from backend.strategies.macd_strategy import MACDStrategy
from backend.strategies.bb_strategy import BollingerStrategy
from backend.strategies.ema_crossover import EMACrossoverStrategy
from backend.ml.ml_strategy import MLStrategy
from backend.strategies.gpt_strategy import GPTSentimentStrategy


class StrategyVoter:
    def __init__(self, symbol: str = "btcusdt"):
        self.symbol = symbol.lower()
        self.strategies = self._initialize_strategies()

    def _initialize_strategies(self) -> List:
        return [
            RSIStrategy(),
            MACDStrategy(),
            EMACrossoverStrategy(),
            BollingerStrategy(),
            MLStrategy(symbol=self.symbol),
            GPTSentimentStrategy(symbol=self.symbol)
        ]

    def get_final_signal(self, df: pd.DataFrame) -> str:
        votes = {"BUY": 0, "SELL": 0, "HOLD": 0}

        if len(df) < 2:
            print("[StrategyVoter] Warning: Not enough data to evaluate (need min 2 rows)")
            return "HOLD"

        print("\n[StrategyVoter] Individual Strategy Signals:")
        current = df.iloc[-1]
        previous = df.iloc[-2]

        for strategy in self.strategies:
            strategy_name = getattr(strategy, 'name', strategy.__class__.__name__)
            try:
                if isinstance(strategy, (MLStrategy, GPTSentimentStrategy)):
                    result = strategy.evaluate(df)
                else:
                    result = strategy.evaluate(current, previous)

                action = self._parse_strategy_result(result)
                votes[action] += 1

                reason = result.get("reason", "No reason") if isinstance(result, dict) else "-"
                print(f" - {strategy_name}: {action} → {reason}")

            except Exception as e:
                print(f" - {strategy_name}: ERROR → {str(e)}")
                votes["HOLD"] += 1

        final = max(votes.keys(), key=lambda k: votes[k])  # fixed max usage
        print(f"\n[StrategyVoter] Votes Summary: {votes} → Final Signal: {final}")
        return final

    def _parse_strategy_result(self, result) -> str:
        if not result:
            return "HOLD"

        if isinstance(result, dict):
            action = result.get("action", "HOLD").upper()
            return action if action in ["BUY", "SELL"] else "HOLD"

        if isinstance(result, str):
            return result.upper() if result.upper() in ["BUY", "SELL"] else "HOLD"

        return "HOLD"
