"""Order lifecycle manager with strict state machine transitions."""
from typing import Dict, List, Optional

from backend.orders.models import Order, OrderStatus, OrderSide
from backend.orders.state_machine import apply_cancel, apply_fill, InvalidOrderTransition


class OrderManager:
    def __init__(self):
        self._orders: Dict[str, Order] = {}

    def submit(self, order: Order) -> Order:
        if order.status != OrderStatus.PENDING:
            order.status = OrderStatus.PENDING
        self._orders[order.id] = order
        return order

    def fill(self, order_id: str, qty: float, price: float) -> Order:
        order = self._orders[order_id]
        apply_fill(order, qty, price)
        return order

    def cancel(self, order_id: str) -> Order:
        order = self._orders[order_id]
        apply_cancel(order)
        return order

    def get(self, order_id: str) -> Optional[Order]:
        return self._orders.get(order_id)

    def list_open(self) -> List[Order]:
        return [o for o in self._orders.values() if o.status in (OrderStatus.PENDING, OrderStatus.PARTIAL)]
