"""PnL handler: compute and broadcast profit/loss updates."""
import logging

from odatrade.core.event_bus_async import AsyncEventBus, Event, EventType
from odatrade.core.redis_state import RedisStateStore
from backend.portfolio.pnl import calculate_trade_pnl

logger = logging.getLogger("odatrade.handler.pnl")


class PnLHandler:
    def __init__(self, bot_id: str, config: dict, bus: AsyncEventBus, state: RedisStateStore):
        self.bot_id = bot_id
        self.config = config
        self.bus = bus
        self.state = state
        self._cumulative_pnl = 0.0
        self._trade_pnls = []

    async def handle(self, event: Event):
        if event.type != EventType.ORDER_FILLED:
            return

        symbol = event.payload.get("symbol")
        side = event.payload.get("side")
        fill_price = event.payload.get("fill_price", 0)
        quantity = event.payload.get("quantity", 0)

        positions = self.state.get_positions(self.bot_id)
        pos = positions.get(symbol, {})
        entry = pos.get("avg_entry", fill_price)

        trade_side = "long" if side == "buy" else "short"
        if side == "sell" and pos.get("quantity", 0) > 0:
            pnl_result = calculate_trade_pnl(entry, fill_price, quantity, trade_side)
            net_pnl = pnl_result["net"]
            self._cumulative_pnl += net_pnl
            self._trade_pnls.append(net_pnl)

            self.state.update_pnl(self.bot_id, symbol, net_pnl, self._cumulative_pnl)
            self.state.increment_metric(self.bot_id, "trades_closed")

            await self.bus.emit(Event(
                type=EventType.PNL_UPDATE,
                bot_id=self.bot_id,
                payload={
                    "symbol": symbol,
                    "pnl": net_pnl,
                    "cumulative": self._cumulative_pnl,
                    "gross": pnl_result["gross"],
                    "fees": pnl_result["fees"],
                    "return_pct": pnl_result["return_pct"],
                    "trade_count": len(self._trade_pnls),
                },
                correlation_id=event.correlation_id,
            ))
            logger.info("[%s] PnL update: %s net=%.4f cumulative=%.4f", self.bot_id, symbol, net_pnl, self._cumulative_pnl)

            max_dd = self.config.get("max_drawdown", 0.15)
            starting = self.config.get("starting_balance", 5000.0)
            if self._cumulative_pnl < -(starting * max_dd):
                await self.bus.emit(Event(
                    type=EventType.KILL_SWITCH,
                    bot_id=self.bot_id,
                    payload={"reason": "max_drawdown_breached", "pnl": self._cumulative_pnl},
                ))
                self.state.increment_metric(self.bot_id, "drawdown_breaches")
