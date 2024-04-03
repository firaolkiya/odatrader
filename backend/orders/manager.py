"""Order lifecycle manager."""
from typing import Dict, List
from backend.orders.models import Order, OrderStatus, OrderSide

class OrderManager:
    def __init__(self):
        self._orders: Dict[str, Order] = {}

    def submit(self, order: Order) -> Order:
        self._orders[order.id] = order
        return order

    def fill(self, order_id: str, qty: float, price: float) -> Order:
        order = self._orders[order_id]
        order.filled_qty += qty
        order.avg_fill_price = price
        order.status = OrderStatus.FILLED if order.filled_qty >= order.quantity else OrderStatus.PARTIAL
        return order

    def cancel(self, order_id: str) -> Order:
        order = self._orders[order_id]
        order.status = OrderStatus.CANCELLED
        return order

    def list_open(self) -> List[Order]:
        return [o for o in self._orders.values() if o.status in (OrderStatus.PENDING, OrderStatus.PARTIAL)]
