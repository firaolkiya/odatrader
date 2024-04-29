import pytest
import pandas as pd

STRATEGY_CASES = [
    ("rsi_oversold", {"rsi": 25, "close": 100}, {"rsi": 30, "close": 100}, "BUY"),
    ("rsi_overbought", {"rsi": 75, "close": 100}, {"rsi": 70, "close": 100}, "SELL"),
    ("rsi_neutral", {"rsi": 50, "close": 100}, {"rsi": 50, "close": 100}, None),
    ("macd_bullish", {"macd": 1, "macd_signal": 0, "close": 100}, {"macd": 0, "macd_signal": 0, "close": 100}, None),
    ("ema_cross_up", {"ema_9": 105, "ema_21": 100, "close": 105}, {"ema_9": 98, "ema_21": 100, "close": 98}, None),
    ("bb_lower", {"close": 90, "bb_lower": 95, "bb_upper": 110}, {"close": 95, "bb_lower": 95, "bb_upper": 110}, None),
    ("stoch_oversold", {"stoch_k": 15, "close": 100}, {"stoch_k": 20, "close": 100}, "BUY"),
    ("stoch_overbought", {"stoch_k": 85, "close": 100}, {"stoch_k": 80, "close": 100}, "SELL"),
    ("adx_uptrend", {"adx": 30, "plus_di": 25, "minus_di": 15, "close": 100}, {}, "BUY"),
    ("adx_downtrend", {"adx": 30, "plus_di": 15, "minus_di": 25, "close": 100}, {}, "SELL"),
    ("vwap_below", {"close": 98, "vwap": 100}, {"close": 99, "vwap": 100}, "BUY"),
    ("vwap_above", {"close": 102, "vwap": 100}, {"close": 101, "vwap": 100}, "SELL"),
    ("momentum_up", {"roc": 3, "close": 100}, {}, "BUY"),
    ("momentum_down", {"roc": -3, "close": 100}, {}, "SELL"),
    ("mean_revert_oversold", {"zscore": -2.5, "close": 100}, {}, "BUY"),
    ("mean_revert_overbought", {"zscore": 2.5, "close": 100}, {}, "SELL"),
]

class TestRSIStrategy:
    @pytest.mark.parametrize("name,current,previous,expected", STRATEGY_CASES[:3])
    def test_rsi(self, name, current, previous, expected):
        from backend.strategies.rsi_strategy import RSIStrategy
        r = RSIStrategy().evaluate(current, previous)
        if expected is None:
            assert r is None
        else:
            assert r["action"] == expected

class TestStochStrategy:
    @pytest.mark.parametrize("name,current,previous,expected", STRATEGY_CASES[6:8])
    def test_stoch(self, name, current, previous, expected):
        from backend.strategies.stoch_strategy import StochasticStrategy
        r = StochasticStrategy().evaluate(current, previous)
        assert r["action"] == expected

class TestADXStrategy:
    @pytest.mark.parametrize("name,current,previous,expected", STRATEGY_CASES[8:10])
    def test_adx(self, name, current, previous, expected):
        from backend.strategies.adx_strategy import ADXStrategy
        r = ADXStrategy().evaluate(current, previous)
        assert r["action"] == expected

class TestVWAPStrategy:
    @pytest.mark.parametrize("name,current,previous,expected", STRATEGY_CASES[10:12])
    def test_vwap(self, name, current, previous, expected):
        from backend.strategies.vwap_strategy import VWAPStrategy
        r = VWAPStrategy().evaluate(current, previous)
        assert r["action"] == expected

class TestMomentumStrategy:
    @pytest.mark.parametrize("name,current,previous,expected", STRATEGY_CASES[12:14])
    def test_momentum(self, name, current, previous, expected):
        from backend.strategies.momentum_strategy import MomentumStrategy
        r = MomentumStrategy().evaluate(current, previous)
        assert r["action"] == expected

class TestMeanRevertStrategy:
    @pytest.mark.parametrize("name,current,previous,expected", STRATEGY_CASES[14:16])
    def test_mean_revert(self, name, current, previous, expected):
        from backend.strategies.mean_revert_strategy import MeanRevertStrategy
        r = MeanRevertStrategy().evaluate(current, previous)
        assert r["action"] == expected

class TestDonchianStrategy:
    def test_breakout_up(self):
        from backend.strategies.donchian_strategy import DonchianStrategy
        r = DonchianStrategy().evaluate({"close": 110, "donchian_upper": 105, "donchian_lower": 90}, {})
        assert r["action"] == "BUY"

    def test_breakout_down(self):
        from backend.strategies.donchian_strategy import DonchianStrategy
        r = DonchianStrategy().evaluate({"close": 85, "donchian_upper": 105, "donchian_lower": 90}, {})
        assert r["action"] == "SELL"

    def test_inside_channel(self):
        from backend.strategies.donchian_strategy import DonchianStrategy
        r = DonchianStrategy().evaluate({"close": 100, "donchian_upper": 105, "donchian_lower": 90}, {})
        assert r["action"] == "HOLD"

class TestGridTrading:
    def test_hold_initially(self):
        from backend.strategies.grid_trading import GridTradingStrategy
        r = GridTradingStrategy().evaluate({"close": 100}, {})
        assert r["action"] == "HOLD"

class TestMarketMaker:
    def test_quoting(self):
        from backend.strategies.market_maker import MarketMakerStrategy
        r = MarketMakerStrategy().evaluate({"close": 100, "bid": 99.9, "ask": 100.1}, {})
        assert r["action"] in ("BUY","SELL","HOLD")

class TestOrderbookImbalance:
    def test_bullish_imbalance(self):
        from backend.strategies.orderbook_imbalance import OrderbookImbalanceStrategy
        r = OrderbookImbalanceStrategy().evaluate({"close": 101}, {"close": 100}, imbalance=0.5)
        assert r["action"] == "BUY"

    def test_bearish_imbalance(self):
        from backend.strategies.orderbook_imbalance import OrderbookImbalanceStrategy
        r = OrderbookImbalanceStrategy().evaluate({"close": 99}, {"close": 100}, imbalance=-0.5)
        assert r["action"] == "SELL"

    def test_compute_imbalance(self):
        from backend.strategies.orderbook_imbalance import OrderbookImbalanceStrategy
        imb = OrderbookImbalanceStrategy.compute_imbalance([(100,10),(99,5)], [(101,2),(102,3)])
        assert imb > 0

class TestComposite:
    def test_aggregate_buy(self):
        from backend.strategies.composite import aggregate_signals
        assert aggregate_signals([{"action":"BUY"},{"action":"BUY"},{"action":"HOLD"}]) == "BUY"

    def test_aggregate_sell(self):
        from backend.strategies.composite import aggregate_signals
        assert aggregate_signals([{"action":"SELL"},{"action":"SELL"}]) == "SELL"

    def test_aggregate_hold(self):
        from backend.strategies.composite import aggregate_signals
        assert aggregate_signals([{"action":"HOLD"}]) == "HOLD"
