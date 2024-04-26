"""Risk handler: validate signals against risk limits before order creation."""
import logging
from datetime import datetime, timezone

from odatrade.core.event_bus_async import AsyncEventBus, Event, EventType
from odatrade.core.redis_state import RedisStateStore

logger = logging.getLogger("odatrade.handler.risk")


class RiskHandler:
    def __init__(self, bot_id: str, config: dict, bus: AsyncEventBus, state: RedisStateStore):
        self.bot_id = bot_id
        self.config = config
        self.bus = bus
        self.state = state
        self._daily_trades = 0
        self._last_reset = datetime.now(timezone.utc).date()

    def _reset_daily_counters(self):
        today = datetime.now(timezone.utc).date()
        if today != self._last_reset:
            self._daily_trades = 0
            self._last_reset = today

    async def handle(self, event: Event):
        if event.type != EventType.STRATEGY_SIGNAL:
            return

        self._reset_daily_counters()
        symbol = event.payload.get("symbol")
        signal = event.payload.get("signal", "HOLD")

        if signal == "HOLD":
            return

        if self.state.is_kill_switch_active(self.bot_id):
            await self._reject(event, "kill_switch_active")
            return

        max_trades = self.config.get("max_trades_per_day", 30)
        if self._daily_trades >= max_trades:
            await self._reject(event, "max_trades_exceeded")
            return

        max_drawdown = self.config.get("max_drawdown", 0.15)
        metrics = self.state.get_metrics(self.bot_id)
        if metrics.get("drawdown_breaches", 0) > 0:
            await self._reject(event, "drawdown_limit")
            return

        from backend.risk.exposure import check_exposure
        positions = self.state.get_positions(self.bot_id)
        exposure_map = {sym: pos.get("quantity", 0) * pos.get("avg_entry", 0) for sym, pos in positions.items()}
        exposure_check = check_exposure(
            exposure_map,
            max_per_symbol=self.config.get("max_per_symbol_exposure", 0.3),
            max_total=self.config.get("max_total_exposure", 1.0),
        )
        if not exposure_check["ok"]:
            await self._reject(event, f"exposure: {exposure_check['violations']}")
            return

        self._daily_trades += 1
        await self.bus.emit(Event(
            type=EventType.RISK_APPROVED,
            bot_id=self.bot_id,
            payload={
                "symbol": symbol,
                "signal": signal,
                "strategy": event.payload.get("strategy"),
                "approved_at": datetime.now(timezone.utc).isoformat(),
            },
            correlation_id=event.correlation_id,
        ))
        self.state.increment_metric(self.bot_id, "risk_approved")

    async def _reject(self, event: Event, reason: str):
        await self.bus.emit(Event(
            type=EventType.RISK_REJECTED,
            bot_id=self.bot_id,
            payload={"reason": reason, "original": event.payload},
            correlation_id=event.correlation_id,
        ))
        self.state.increment_metric(self.bot_id, "risk_rejected")
        logger.warning("[%s] Risk rejected: %s", self.bot_id, reason)
