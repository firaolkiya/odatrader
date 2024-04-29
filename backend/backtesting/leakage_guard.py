"""Detect and block lookahead bias during walk-forward / backtest runs."""
import inspect
from typing import Callable

import pandas as pd


class LookaheadViolation(Exception):
    pass


class LeakageGuard:
    """Ensures signal_fn only receives history up to the current bar index."""

    def __init__(self):
        self._bar_index = 0

    def set_bar(self, index: int):
        self._bar_index = index

    def wrap(self, signal_fn: Callable) -> Callable:
        params = inspect.signature(signal_fn).parameters
        accepts_history = "history" in params

        def guarded(row, prev_row=None, history=None, **_kwargs):
            if history is not None:
                allowed = self._bar_index + 1
                if len(history) > allowed:
                    raise LookaheadViolation(
                        f"history length {len(history)} exceeds allowed {allowed} at bar {self._bar_index}"
                    )
            if accepts_history:
                return signal_fn(row, prev_row, history=history)
            return signal_fn(row, prev_row)

        return guarded


def run_guarded_backtest(engine, df: pd.DataFrame, signal_fn: Callable) -> dict:
    """Run backtest with per-bar history slices and leakage validation."""
    guard = LeakageGuard()
    wrapped = guard.wrap(signal_fn)
    return engine.run(df, wrapped, strict_no_lookahead=True, leakage_guard=guard)
