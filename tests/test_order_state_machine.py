import pytest
from backend.orders.manager import OrderManager
from backend.orders.models import Order, OrderSide, OrderStatus
from backend.orders.state_machine import InvalidOrderTransition, apply_fill, can_transition


class TestTransitions:
    def test_pending_to_partial(self):
        assert can_transition(OrderStatus.PENDING, OrderStatus.PARTIAL)

    def test_filled_terminal(self):
        assert not can_transition(OrderStatus.FILLED, OrderStatus.CANCELLED)

    def test_vwap_partial_fills(self):
        o = Order("btcusdt", OrderSide.BUY, 1.0)
        apply_fill(o, 0.25, 100.0)
        apply_fill(o, 0.75, 104.0)
        assert o.status == OrderStatus.FILLED
        assert abs(o.avg_fill_price - 103.0) < 0.01

    def test_reject_overfill(self):
        o = Order("btcusdt", OrderSide.BUY, 1.0)
        with pytest.raises(ValueError):
            apply_fill(o, 1.5, 100.0)

    def test_reject_cancel_then_fill(self):
        m = OrderManager()
        o = Order("btcusdt", OrderSide.BUY, 1.0)
        m.submit(o)
        m.cancel(o.id)
        with pytest.raises(InvalidOrderTransition):
            m.fill(o.id, 0.5, 100.0)
