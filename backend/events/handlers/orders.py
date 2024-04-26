"""Order handler: create and fill orders from approved signals."""
import logging
from datetime import datetime, timezone

from odatrade.core.event_bus_async import AsyncEventBus, Event, EventType
from odatrade.core.redis_state import RedisStateStore
from backend.orders.manager import OrderManager
from backend.orders.models import Order, OrderSide

logger = logging.getLogger("odatrade.handler.orders")


class OrderHandler:
    def __init__(self, bot_id: str, config: dict, bus: AsyncEventBus, state: RedisStateStore):
        self.bot_id = bot_id
        self.config = config
        self.bus = bus
        self.state = state
        self.order_manager = OrderManager()
        self.starting_balance = config.get("starting_balance", 5000.0)

    async def handle(self, event: Event):
        if event.type != EventType.RISK_APPROVED:
            return

        symbol = event.payload.get("symbol")
        signal = event.payload.get("signal")
        if not symbol or signal not in ("BUY", "SELL"):
            return

        side = OrderSide.BUY if signal == "BUY" else OrderSide.SELL
        risk_pct = self.config.get("fixed_risk_pct", 0.01)
        price = event.payload.get("price", 0)
        if not price:
            positions = self.state.get_positions(self.bot_id)
            pos = positions.get(symbol, {})
            price = pos.get("last_price", 100)

        qty = (self.starting_balance * risk_pct) / price if price else 0
        if qty <= 0:
            return

        order = Order(symbol=symbol, side=side, quantity=qty, price=price)
        self.order_manager.submit(order)

        await self.bus.emit(Event(
            type=EventType.ORDER_CREATED,
            bot_id=self.bot_id,
            payload={
                "order_id": order.id,
                "symbol": symbol,
                "side": side.value,
                "quantity": qty,
                "price": price,
            },
            correlation_id=event.correlation_id,
        ))

        filled = self.order_manager.fill(order.id, qty, price)
        self.state.set_position(self.bot_id, symbol, {
            "quantity": qty if side == OrderSide.BUY else -qty,
            "avg_entry": price,
            "last_price": price,
            "side": side.value,
        })

        await self.bus.emit(Event(
            type=EventType.ORDER_FILLED,
            bot_id=self.bot_id,
            payload={
                "order_id": order.id,
                "symbol": symbol,
                "side": side.value,
                "quantity": qty,
                "fill_price": price,
                "filled_at": datetime.now(timezone.utc).isoformat(),
            },
            correlation_id=event.correlation_id,
        ))
        self.state.increment_metric(self.bot_id, "orders_filled")
        logger.info("[%s] Order filled: %s %s %.4f @ %.2f", self.bot_id, side.value, symbol, qty, price)
