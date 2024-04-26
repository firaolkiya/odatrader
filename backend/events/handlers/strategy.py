"""Strategy handler: evaluate strategies and emit signals."""
import logging

from odatrade.core.event_bus_async import AsyncEventBus, Event, EventType
from odatrade.core.redis_state import RedisStateStore

logger = logging.getLogger("odatrade.handler.strategy")


class StrategyHandler:
    def __init__(self, bot_id: str, config: dict, bus: AsyncEventBus, state: RedisStateStore):
        self.bot_id = bot_id
        self.config = config
        self.bus = bus
        self.state = state
        self._voters = {}

    def _get_voter(self, symbol: str):
        if symbol not in self._voters:
            from backend.strategies.strategy_voter import StrategyVoter
            self._voters[symbol] = StrategyVoter(symbol)
        return self._voters[symbol]

    async def handle(self, event: Event):
        symbol = event.payload.get("symbol")
        features = event.payload.get("features")
        df_tail = event.payload.get("dataframe_tail", [])

        if not symbol or not features:
            return

        try:
            import pandas as pd
            import yaml
            df = pd.DataFrame(df_tail) if df_tail else pd.DataFrame([features])
            if len(df) < 2:
                df = pd.concat([df, df], ignore_index=True)

            adaptive_config = {}
            try:
                with open("config/adaptive.yaml") as f:
                    adaptive_config = yaml.safe_load(f).get("strategy", {})
            except FileNotFoundError:
                pass

            from backend.engine.adaptive_voter import AdaptiveVoter
            voter = AdaptiveVoter(symbol, adaptive_config)
            snap = voter.evaluate(df)
            signal = snap.action

            self.state.publish_signal(self.bot_id, {
                "symbol": symbol, "signal": signal,
                "strategy": "adaptive_voter", "regime": snap.regime,
                "bull_share": snap.bull_share, "entry_threshold": snap.entry_threshold,
            })
            self.state.increment_metric(self.bot_id, "signals_generated")

            from backend.audit.decision_logger import DecisionLogger
            DecisionLogger().log_signal(snap)

            await self.bus.emit(Event(
                type=EventType.STRATEGY_SIGNAL,
                bot_id=self.bot_id,
                payload={
                    "symbol": symbol, "signal": signal,
                    "strategy": "adaptive_voter",
                    "regime": snap.regime, "bull_share": snap.bull_share,
                    "bear_share": snap.bear_share,
                    "entry_threshold": snap.entry_threshold,
                    "exit_threshold": snap.exit_threshold,
                    "votes": [v.to_dict() for v in snap.votes],
                    "reason": snap.reason,
                },
                correlation_id=event.correlation_id,
            ))
            logger.info("[%s] %s adaptive signal: %s (regime=%.2f)", self.bot_id, symbol, signal, snap.regime)
        except Exception as e:
            logger.error("[%s] Strategy evaluation failed: %s", self.bot_id, e)
            self.state.increment_metric(self.bot_id, "strategy_errors")
