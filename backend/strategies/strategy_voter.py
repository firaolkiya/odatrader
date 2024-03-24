# backend/strategy/strategy_voter.py
import os,sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.strategies.rsi_strategy import RSIStrategy
from backend.strategies.macd_strategy import MACDStrategy
from backend.strategies.bb_strategy import BollingerBandsStrategy
from backend.strategies.ema_crossover import EMACrossoverStrategy
from backend.ml.ml_strategy import MLStrategy

class StrategyVoter:
    def __init__(self):
        self.strategies = [
            RSIStrategy(),
            MACDStrategy(),
            EMACrossoverStrategy(),
            BollingerBandsStrategy(),
            MLStrategy()
        ]


    def get_final_signal(self, df) -> str:
        votes = {"BUY": 0, "SELL": 0, "HOLD": 0}

        if len(df) < 2:
            print("[StrategyVoter] Not enough data to evaluate.")
            return "HOLD"

        latest = df.iloc[-1]
        previous = df.iloc[-2]

        for strategy in self.strategies:
            try:
                result = strategy.evaluate(latest, previous)
                if result and result.get("action"):
                    action = result["action"].upper()
                    if action in votes:
                        votes[action] += 1
            except Exception as e:
                print(f"[StrategyVoter] Strategy {strategy.name} error: {e}")

        final = max(votes, key=votes.get)
        print(f"[StrategyVoter] Votes: {votes} → Final Signal: {final}")
        return final
