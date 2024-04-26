"""Adaptive confidence voting engine with regime-aware thresholds."""
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
import pandas as pd

from backend.core.signals import SignalVote, SignalSnapshot
from backend.engine.regime_classifier import RegimeClassifier

logger = logging.getLogger("odatrade.adaptive_voter")


class AdaptiveVoter:
    """
    Dynamic confidence voting per Milestone 3 spec:
    entry_threshold = base_entry - entry_slope * regime
    exit_threshold  = base_exit  + exit_slope  * regime
    """

    def __init__(self, symbol: str, config: dict = None):
        self.symbol = symbol
        self.config = config or self._default_config()
        self.regime_classifier = RegimeClassifier(self.config)
        self._strategies = self._load_strategies()

    def _default_config(self) -> dict:
        return {
            "weights": {
                "rsi": 0.15, "ema_cross": 0.20, "macd": 0.15,
                "supertrend": 0.15, "bollinger": 0.10, "ob_imbalance": 0.10, "ml_trend": 0.15,
            },
            "base_entry": 0.70, "base_exit": 0.50,
            "entry_slope": 0.20, "exit_slope": 0.10,
            "sl_atr_mult": {"calm": 1.5, "volatile": 2.8},
            "tp_rr": 1.6,
        }

    def _load_strategies(self) -> dict:
        strategies = {}
        try:
            from backend.strategies.rsi_strategy import RSIStrategy
            from backend.strategies.macd_strategy import MACDStrategy
            from backend.strategies.ema_crossover import EMACrossoverStrategy
            from backend.strategies.bb_strategy import BollingerStrategy
            from backend.strategies.supertrend_strategy import SupertrendStrategy
            from backend.strategies.orderbook_imbalance import OrderbookImbalanceStrategy
            from backend.ml.ml_strategy import MLStrategy
            strategies = {
                "rsi": RSIStrategy(), "macd": MACDStrategy(),
                "ema_cross": EMACrossoverStrategy(), "bollinger": BollingerStrategy(),
                "supertrend": SupertrendStrategy(), "ob_imbalance": OrderbookImbalanceStrategy(),
                "ml_trend": MLStrategy(symbol=self.symbol),
            }
        except ImportError as e:
            logger.warning("Strategy load partial: %s", e)
        return strategies

    def _vote_from_result(self, result) -> int:
        if not result:
            return 0
        action = result.get("action", "HOLD") if isinstance(result, dict) else str(result)
        action = action.upper()
        if action == "BUY":
            return 1
        if action == "SELL":
            return -1
        return 0

    def evaluate(self, df: pd.DataFrame, ob_imbalance: float = 0.0) -> SignalSnapshot:
        regime_info = self.regime_classifier.classify(df)
        regime = regime_info["regime"]

        entry_th = self.config["base_entry"] - self.config["entry_slope"] * regime
        exit_th = self.config["base_exit"] + self.config["exit_slope"] * regime

        weights = self.config.get("weights", {})
        votes: List[SignalVote] = []
        current = df.iloc[-1] if len(df) > 0 else {}
        previous = df.iloc[-2] if len(df) > 1 else current

        for name, strategy in self._strategies.items():
            weight = weights.get(name, 0.1)
            try:
                if name == "ob_imbalance":
                    result = strategy.evaluate(current, previous, imbalance=ob_imbalance)
                elif name == "ml_trend":
                    result = strategy.evaluate(self.symbol)
                else:
                    result = strategy.evaluate(current, previous)
                val = self._vote_from_result(result)
                reason = result.get("reason", "") if isinstance(result, dict) else ""
                votes.append(SignalVote(name=name, value=val, weight=weight, details=reason))
            except Exception as e:
                votes.append(SignalVote(name=name, value=0, weight=weight, details=str(e)))

        total_weight = sum(v.weight for v in votes) or 1.0
        bull = sum(v.weight for v in votes if v.value == 1)
        bear = sum(v.weight for v in votes if v.value == -1)
        bull_share = bull / total_weight
        bear_share = bear / total_weight

        action = "HOLD"
        reason = f"regime={regime:.2f} entry_th={entry_th:.2f} exit_th={exit_th:.2f}"
        if bull_share >= entry_th:
            action = "BUY"
            reason = f"Bullish {bull_share:.1%} >= entry {entry_th:.1%} ({regime_info['label']})"
        elif bear_share >= exit_th:
            action = "SELL"
            reason = f"Bearish {bear_share:.1%} >= exit {exit_th:.1%} ({regime_info['label']})"

        return SignalSnapshot(
            ts=datetime.now(timezone.utc).isoformat(),
            instrument=self.symbol,
            votes=votes,
            bull_share=bull_share,
            bear_share=bear_share,
            score=bull_share,
            regime=regime,
            entry_threshold=entry_th,
            exit_threshold=exit_th,
            action=action,
            reason=reason,
        )
