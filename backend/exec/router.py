"""Execution router: order management with risk checks, retries, paper/live modes."""
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from backend.core.signals import TradeIntent
from backend.orders.models import Order, OrderSide, OrderStatus
from backend.orders.manager import OrderManager
from backend.exec.fee_model import FeeModel
from backend.exec.slippage import SlippageModel
from backend.audit.decision_logger import DecisionLogger

logger = logging.getLogger("odatrade.exec")


class ExecutionRouter:
    """EMS: routes orders to gateway/broker with pre-trade risk checks."""

    def __init__(self, config: dict = None, mode: str = "paper"):
        self.config = config or {}
        self.mode = mode  # "paper" or "live"
        self.order_manager = OrderManager()
        self.fee_model = FeeModel()
        self.slippage_model = SlippageModel()
        self.decision_logger = DecisionLogger()
        self._last_trade_time: Dict[str, float] = {}
        self._sl_cooldown: Dict[str, float] = {}
        self._orders_per_minute: List[float] = []
        self.min_inter_trade_delay = self.config.get("min_inter_trade_delay", 5.0)
        self.sl_cooldown_sec = self.config.get("sl_cooldown_sec", 300)
        self.max_orders_per_min = self.config.get("max_orders_per_min", 10)
        self._gateways: Dict[str, object] = {}

    def set_gateway(self, venue: str, gateway):
        self._gateways[venue] = gateway

    def _can_trade(self, symbol: str) -> tuple:
        now = time.time()
        last = self._last_trade_time.get(symbol, 0)
        if now - last < self.min_inter_trade_delay:
            return False, f"inter-trade delay ({self.min_inter_trade_delay}s)"
        cooldown_until = self._sl_cooldown.get(symbol, 0)
        if now < cooldown_until:
            return False, f"SL cooldown until {cooldown_until - now:.0f}s"
        self._orders_per_minute = [t for t in self._orders_per_minute if now - t < 60]
        if len(self._orders_per_minute) >= self.max_orders_per_min:
            return False, "max orders per minute exceeded"
        return True, "ok"

    async def route_intent(self, intent: TradeIntent, venue: str = "binance") -> dict:
        can, reason = self._can_trade(intent.instrument)
        if not can:
            self.decision_logger.log_reject(intent, reason)
            return {"status": "rejected", "reason": reason}

        side = OrderSide.BUY if intent.side.upper() == "BUY" else OrderSide.SELL
        order = Order(
            symbol=intent.instrument, side=side, quantity=intent.size,
            price=intent.px_hint, id=str(uuid.uuid4())[:12],
        )

        fill_price = intent.px_hint or 100.0
        if intent.order_type == "market":
            fill_price = self.slippage_model.apply(fill_price, intent.size, side="buy" if side == OrderSide.BUY else "sell")
        elif intent.post_only and intent.px_hint:
            fill_price = intent.px_hint

        fees = self.fee_model.compute(fill_price, intent.size, maker=intent.post_only)

        if self.mode == "live" and venue in self._gateways:
            gw = self._gateways[venue]
            result = await gw.place_order(order)
            self.decision_logger.log_order(intent, order, result)
            self._last_trade_time[intent.instrument] = time.time()
            self._orders_per_minute.append(time.time())
            return result

        self.order_manager.submit(order)
        filled = self.order_manager.fill(order.id, intent.size, fill_price)
        self._last_trade_time[intent.instrument] = time.time()
        self._orders_per_minute.append(time.time())

        result = {
            "status": "filled", "mode": self.mode,
            "order_id": order.id, "fill_price": fill_price,
            "fees": fees, "quantity": intent.size,
            "filled_at": datetime.now(timezone.utc).isoformat(),
        }
        self.decision_logger.log_fill(intent, order, result)
        return result

    def report_stop_loss(self, symbol: str):
        self._sl_cooldown[symbol] = time.time() + self.sl_cooldown_sec

    def set_mode(self, mode: str):
        if mode in ("paper", "live"):
            self.mode = mode
            logger.info("Execution mode set to %s", mode)
