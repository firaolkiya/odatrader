"""Strict order lifecycle state machine with validated transitions."""
from backend.orders.models import Order, OrderStatus


class InvalidOrderTransition(Exception):
    def __init__(self, order_id: str, from_status: OrderStatus, to_status: OrderStatus):
        super().__init__(f"order {order_id}: {from_status.value} -> {to_status.value} not allowed")
        self.order_id = order_id
        self.from_status = from_status
        self.to_status = to_status


_ALLOWED = {
    OrderStatus.PENDING: {OrderStatus.PARTIAL, OrderStatus.FILLED, OrderStatus.CANCELLED},
    OrderStatus.PARTIAL: {OrderStatus.PARTIAL, OrderStatus.FILLED, OrderStatus.CANCELLED},
    OrderStatus.FILLED: set(),
    OrderStatus.CANCELLED: set(),
}


def can_transition(current: OrderStatus, target: OrderStatus) -> bool:
    return target in _ALLOWED.get(current, set())


def apply_fill(order: Order, qty: float, price: float) -> OrderStatus:
    if order.status == OrderStatus.CANCELLED:
        raise InvalidOrderTransition(order.id, order.status, OrderStatus.FILLED)
    if qty <= 0:
        raise ValueError("fill quantity must be positive")

    remaining = order.quantity - order.filled_qty
    if qty > remaining + 1e-12:
        raise ValueError(f"fill {qty} exceeds remaining {remaining}")

    notional = (order.avg_fill_price * order.filled_qty) + (price * qty)
    order.filled_qty += qty
    order.avg_fill_price = notional / order.filled_qty if order.filled_qty else 0.0

    target = OrderStatus.FILLED if order.filled_qty >= order.quantity else OrderStatus.PARTIAL
    if not can_transition(order.status, target):
        raise InvalidOrderTransition(order.id, order.status, target)
    order.status = target
    return order.status


def apply_cancel(order: Order) -> OrderStatus:
    if order.status in (OrderStatus.FILLED, OrderStatus.CANCELLED):
        raise InvalidOrderTransition(order.id, order.status, OrderStatus.CANCELLED)
    if not can_transition(order.status, OrderStatus.CANCELLED):
        raise InvalidOrderTransition(order.id, order.status, OrderStatus.CANCELLED)
    order.status = OrderStatus.CANCELLED
    return order.status
