"""Composite signal aggregator."""
from typing import List, Dict

def aggregate_signals(signals: List[Dict], weights: List[float] = None) -> str:
    votes = {"BUY": 0.0, "SELL": 0.0, "HOLD": 0.0}
    weights = weights or [1.0] * len(signals)
    for sig, w in zip(signals, weights):
        action = sig.get("action", "HOLD").upper()
        votes[action] = votes.get(action, 0) + w
    return max(votes, key=votes.get)
