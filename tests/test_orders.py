import pytest
from backend.orders.models import Order, OrderSide, OrderStatus
from backend.orders.manager import OrderManager
from backend.orders.order_book import OrderBook

class TestOrderModel:
    def test_create(self):
        o = Order("btcusdt", OrderSide.BUY, 0.1, price=50000)
        assert o.status == OrderStatus.PENDING

    def test_has_id(self):
        o = Order("btcusdt", OrderSide.BUY, 0.1)
        assert o.id is not None

class TestOrderManager:
    @pytest.fixture
    def mgr(self):
        return OrderManager()

    def test_submit(self, mgr):
        o = Order("btcusdt", OrderSide.BUY, 0.1)
        assert mgr.submit(o).status == OrderStatus.PENDING

    def test_fill(self, mgr):
        o = Order("btcusdt", OrderSide.BUY, 0.1)
        mgr.submit(o)
        filled = mgr.fill(o.id, 0.1, 50000)
        assert filled.status == OrderStatus.FILLED

    def test_partial_fill(self, mgr):
        o = Order("btcusdt", OrderSide.BUY, 1.0)
        mgr.submit(o)
        filled = mgr.fill(o.id, 0.5, 50000)
        assert filled.status == OrderStatus.PARTIAL
        assert filled.avg_fill_price == 50000

    def test_vwap_two_fills(self, mgr):
        o = Order("btcusdt", OrderSide.BUY, 1.0)
        mgr.submit(o)
        mgr.fill(o.id, 0.4, 100.0)
        filled = mgr.fill(o.id, 0.6, 110.0)
        assert filled.status == OrderStatus.FILLED
        assert abs(filled.avg_fill_price - 106.0) < 0.01

    def test_cancel(self, mgr):
        o = Order("btcusdt", OrderSide.BUY, 0.1)
        mgr.submit(o)
        cancelled = mgr.cancel(o.id)
        assert cancelled.status == OrderStatus.CANCELLED

    def test_list_open(self, mgr):
        mgr.submit(Order("btc", OrderSide.BUY, 1))
        mgr.submit(Order("eth", OrderSide.SELL, 2))
        assert len(mgr.list_open()) == 2

class TestOrderBook:
    def test_spread(self):
        ob = OrderBook("btcusdt")
        ob.add_bid(100, 10)
        ob.add_ask(101, 10)
        assert ob.spread() == 1

    def test_best_bid(self):
        ob = OrderBook("btcusdt")
        ob.add_bid(100, 10)
        ob.add_bid(99, 5)
        assert ob.best_bid()[0] == 100
