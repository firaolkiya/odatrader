import pytest
from backend.exec.fee_model import FeeModel
from backend.exec.slippage import SlippageModel
from backend.exec.router import ExecutionRouter
from backend.core.signals import TradeIntent

class TestFeeModel:
    def test_taker_fee(self):
        f = FeeModel()
        fee = f.compute(100, 1.0, maker=False)
        assert fee > 0

    def test_maker_fee_lower(self):
        f = FeeModel(maker_rate=0.0002, taker_rate=0.00075)
        assert f.compute(100, 1, maker=True) < f.compute(100, 1, maker=False)

    def test_fee_scales_with_size(self):
        f = FeeModel()
        assert f.compute(100, 2) > f.compute(100, 1)

    @pytest.mark.parametrize("price,qty", [(100,1),(50000,0.01),(1,1000)])
    def test_various_sizes(self, price, qty):
        f = FeeModel()
        assert f.compute(price, qty) >= 0

class TestSlippageModel:
    def test_buy_slippage_increases_price(self):
        s = SlippageModel()
        assert s.apply(100, 1, "buy") > 100

    def test_sell_slippage_decreases_price(self):
        s = SlippageModel()
        assert s.apply(100, 1, "sell") < 100

    def test_larger_order_more_slippage(self):
        s = SlippageModel()
        assert s.apply(100, 100, "buy") > s.apply(100, 1, "buy")

    def test_simulate_fill(self):
        s = SlippageModel()
        px, qty = s.simulate_fill(100, 5, [(99,10),(98,10)], [(101,10),(102,10)], "buy")
        assert px > 0 and qty > 0

class TestExecutionRouter:
    @pytest.fixture
    def router(self):
        return ExecutionRouter(mode="paper")

    def test_paper_mode(self, router):
        assert router.mode == "paper"

    def test_can_trade_initially(self, router):
        ok, _ = router._can_trade("btcusdt")
        assert ok

    def test_inter_trade_delay(self, router):
        router._last_trade_time["btcusdt"] = __import__("time").time()
        ok, reason = router._can_trade("btcusdt")
        assert not ok

    @pytest.mark.asyncio
    async def test_route_intent_paper(self, router):
        intent = TradeIntent(ts="2025", instrument="btcusdt", side="BUY", size=0.01, px_hint=50000)
        result = await router.route_intent(intent)
        assert result["status"] == "filled"

    def test_set_mode(self, router):
        router.set_mode("live")
        assert router.mode == "live"

    def test_sl_cooldown(self, router):
        router.report_stop_loss("btcusdt")
        ok, _ = router._can_trade("btcusdt")
        assert not ok
