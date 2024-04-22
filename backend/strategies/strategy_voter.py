"""OdaTrade strategy voting engine."""
import os
import sys
from typing import Dict, List
import pandas as pd
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.strategies.rsi_strategy import RSIStrategy
from backend.strategies.macd_strategy import MACDStrategy
from backend.strategies.bb_strategy import BollingerStrategy
from backend.strategies.ema_crossover import EMACrossoverStrategy
from backend.ml.ml_strategy import MLStrategy
from backend.strategies.gpt_strategy import GPTStrategy


class StrategyVoter:
    def __init__(self, symbol: str = "btcusdt"):
        print(f"\n[StrategyVoter] Initializing for {symbol.upper()}")
        self.symbol = symbol.lower()
        self.strategies = self._initialize_strategies()
        self.weights = {
            "CombinedTechnicalStrategy": 0.3,  # Combined weight of all technical strategies
            "MLStrategy": 0.35,
            "GPTStrategy": 0.35
        }
        self.decision_threshold = 0.6  # 60% confidence required

    def _initialize_strategies(self) -> List:
        return [
            RSIStrategy(),  # Still kept for internal use
            MACDStrategy(),  # Still kept for internal use
            EMACrossoverStrategy(),  # Still kept for internal use
            BollingerStrategy(),  # Still kept for internal use
            MLStrategy(symbol=self.symbol),
            GPTStrategy(symbol=self.symbol)
        ]

    def get_final_signal(self, df: pd.DataFrame) -> str:
        if len(df) < 2:
            print("[StrategyVoter] Warning: Not enough data to evaluate (need min 2 rows)")
            return "HOLD"

        print("\n[StrategyVoter] Collecting Strategy Signals:")
        current = df.iloc[-1]
        previous = df.iloc[-2]

        # Phase 1: Get combined technical signal
        tech_signal = self._get_combined_technical_signal(current, previous)
        
        # Phase 2: Get ML and GPT signals
        ml_signal = self._get_ml_signal()
        gpt_signal = self._get_gpt_signal()
        
        # Phase 3: Weighted Voting
        final_signal = self._calculate_weighted_vote(
            tech_signal,
            ml_signal,
            gpt_signal
        )
        
        print(f"\n[StrategyVoter] Final Signal: {final_signal}")
        return final_signal

    def _get_combined_technical_signal(self, current, previous) -> Dict:
        """Evaluate and combine all technical indicators into one signal"""
        signals = []
        buy_count = 0
        sell_count = 0
        
        # Evaluate each technical strategy
        for strategy in self.strategies[:4]:  # First 4 are technical
            strategy_name = strategy.__class__.__name__
            try:
                result = strategy.evaluate(current, previous)
                action = self._parse_strategy_result(result)
                signals.append(f"{strategy_name}: {action}")
                
                if action == "BUY":
                    buy_count += 1
                elif action == "SELL":
                    sell_count += 1
                    
            except Exception as e:
                print(f" - {strategy_name}: ERROR → {str(e)}")
                signals.append(f"{strategy_name}: ERROR")
        
        # Determine combined action
        if buy_count > 1 and sell_count:
            action = "BUY"
        elif sell_count > 1 and buy_count:
            action = "SELL"
        else:
            action = "HOLD"
            
        print(f" - CombinedTechnicalStrategy: {action} ({self.weights['CombinedTechnicalStrategy']} weight)")
        return {
            "action": action,
            "weight": self.weights["CombinedTechnicalStrategy"],
            "reason": " | ".join(signals)
        }

    def _get_ml_signal(self):
        """Get ML strategy signal"""
        ml_strategy = next(s for s in self.strategies if isinstance(s, MLStrategy))
        try:
            result = ml_strategy.evaluate(self.symbol)
            action = self._parse_strategy_result(result)
            print(f" - MLStrategy: {action} ({self.weights['MLStrategy']} weight)")
            return {
                "action": action,
                "weight": self.weights["MLStrategy"],
                "reason": result.get("reason", "No reason") if isinstance(result, dict) else "-"
            }
        except Exception as e:
            print(f" - MLStrategy: ERROR → {str(e)}")
            return {"action": "HOLD", "weight": 0}

    def _get_gpt_signal(self):
        """Get GPT strategy signal"""
        gpt_strategy = next(s for s in self.strategies if isinstance(s, GPTStrategy))
        try:
            print("\n[StrategyVoter] Evaluating GPTStrategy...")
            result = gpt_strategy.evaluate()
            action = self._parse_strategy_result(result)
            print(f" - GPTStrategy: {action} ({self.weights['GPTStrategy']} weight)")
            return {
                "action": action,
                "weight": self.weights["GPTStrategy"],
                "reason": result.get("reason", "No reason") if isinstance(result, dict) else "-"
            }
        except Exception as e:
            print(f" - GPTStrategy: ERROR → {str(e)}")
            return {"action": "HOLD", "weight": 0}

    def _calculate_weighted_vote(self, tech_signal, ml_signal, gpt_signal) -> str:
        """Calculate final weighted decision"""
        weighted_votes = {"BUY": 0.0, "SELL": 0.0, "HOLD": 0.0}
        
        # Add votes from each strategy
        weighted_votes[tech_signal["action"]] += tech_signal["weight"]
        weighted_votes[ml_signal["action"]] += ml_signal["weight"]
        weighted_votes[gpt_signal["action"]] += gpt_signal["weight"]
        
        print(f"\n[StrategyVoter] Weighted Votes: {weighted_votes}")
        
        # Decision rules
        max_action = max(weighted_votes, key=weighted_votes.get)
        max_score = weighted_votes[max_action]
        
        if max_score >= self.decision_threshold:
            return max_action
        
        # Default to HOLD if no clear consensus
        return "HOLD"

    def _parse_strategy_result(self, result) -> str:
        """Parse strategy output into BUY/SELL/HOLD"""
        if not result:
            return "HOLD"

        if isinstance(result, dict):
            action = result.get("action", "").upper()
            return action if action in ("BUY", "SELL") else "HOLD"

        if isinstance(result, str):
            action = result.upper()
            return action if action in ("BUY", "SELL") else "HOLD"

        return "HOLD"